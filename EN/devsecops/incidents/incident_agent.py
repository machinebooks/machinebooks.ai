# Source: The DevSecOps and the Machine -- Chapter 20
# Pattern: Incident correlation, containment, and postmortem agent

import anthropic
from datetime import datetime, timezone
from typing import Any

client = anthropic.Anthropic()

# Tool definitions for the incident response agent
incident_tools = [
    {
        "name": "correlate_alerts",
        "description": (
            "Correlates security alerts from multiple sources "
            "(Falco, pipeline, WAF) within a given time period. "
            "Returns alerts grouped by probable attack vector."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "time_window_minutes": {
                    "type": "integer",
                    "description": "Time window in minutes for correlation"
                },
                "sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Alert sources: falco, pipeline, waf, ids"
                }
            },
            "required": ["time_window_minutes", "sources"]
        }
    },
    {
        "name": "query_sbom",
        "description": (
            "Queries the SBOM of the affected service to identify "
            "vulnerable dependencies related to the incident."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "service_name": {"type": "string"},
                "cve_id": {"type": "string", "description": "Specific CVE to search for, optional"}
            },
            "required": ["service_name"]
        }
    },
    {
        "name": "isolate_container",
        "description": (
            "Isolates a container from the network, applying a network policy "
            "that blocks all traffic except monitoring. "
            "REQUIRES human approval."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "container_id": {"type": "string"},
                "namespace": {"type": "string"},
                "reason": {"type": "string"}
            },
            "required": ["container_id", "namespace", "reason"]
        }
    },
    {
        "name": "request_human_approval",
        "description": (
            "Sends an approval request to the incident channel "
            "with the proposed action details. Blocks until "
            "approval or rejection is received."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action_summary": {"type": "string"},
                "impact_description": {"type": "string"},
                "urgency": {
                    "type": "string",
                    "enum": ["critical", "high", "medium"]
                }
            },
            "required": ["action_summary", "impact_description", "urgency"]
        }
    },
    {
        "name": "generate_postmortem",
        "description": (
            "Generates a structured post-mortem draft from "
            "the incident timeline, actions taken, and metrics."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "incident_id": {"type": "string"},
                "include_metrics": {"type": "boolean", "default": True}
            },
            "required": ["incident_id"]
        }
    }
]

from dataclasses import dataclass, field
from enum import Enum

class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class SecurityAlert:
    source: str            # falco, pipeline, waf, ids
    timestamp: str         # ISO 8601
    severity: Severity
    description: str
    container_id: str | None = None
    service_name: str | None = None
    cve_id: str | None = None
    raw_data: dict = field(default_factory=dict)

@dataclass
class CorrelatedIncident:
    incident_id: str
    alerts: list[SecurityAlert]
    probable_vector: str        # Attack vector hypothesis
    affected_services: list[str]
    timeline: list[dict]        # Chronologically ordered events
    severity: Severity
    recommended_actions: list[str]

def correlate_alerts(
    alerts: list[SecurityAlert],
    time_window_minutes: int = 15
) -> list[CorrelatedIncident]:
    """Groups alerts by temporal proximity and affected services."""
    # Sort by timestamp
    sorted_alerts = sorted(alerts, key=lambda a: a.timestamp)

    # Grouping by time window and service
    clusters: list[list[SecurityAlert]] = []
    current_cluster: list[SecurityAlert] = []

    for alert in sorted_alerts:
        if not current_cluster:
            current_cluster.append(alert)
            continue
        # If the alert falls within the window, add it to the cluster
        time_diff = _minutes_between(current_cluster[-1].timestamp, alert.timestamp)
        if time_diff <= time_window_minutes:
            current_cluster.append(alert)
        else:
            clusters.append(current_cluster)
            current_cluster = [alert]

    if current_cluster:
        clusters.append(current_cluster)

    # Convert clusters into correlated incidents
    incidents = []
    for i, cluster in enumerate(clusters):
        affected = list({a.service_name for a in cluster if a.service_name})
        max_sev = max(cluster, key=lambda a: _severity_rank(a.severity))
        incidents.append(CorrelatedIncident(
            incident_id=f"INC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{i+1:03d}",
            alerts=cluster,
            probable_vector="pending_analysis",  # Claude will enrich this
            affected_services=affected,
            timeline=[{"time": a.timestamp, "event": a.description} for a in cluster],
            severity=max_sev.severity,
            recommended_actions=[]  # Claude will generate these
        ))
    return incidents

def run_incident_agent(incident: CorrelatedIncident) -> dict:
    """Run the response agent on a correlated incident."""

    system_prompt = """You are a security incident response agent.
Your role is to analyze incidents, propose containment actions, and generate
documentation. CRITICAL RULES:
1. NEVER execute destructive actions without prior request_human_approval.
2. Use correlate_alerts to understand scope before proposing containment.
3. Query query_sbom to check for known CVEs involved.
4. Document each decision with technical justification.
5. If severity is CRITICAL, prioritize containment over exhaustive analysis.
6. Generate the post-mortem upon completion, including timeline and recommendations."""

    # Build the initial message with the incident context
    incident_context = format_incident_for_agent(incident)

    messages = [
        {"role": "user", "content": (
            f"A security incident has been detected:\n\n"
            f"{incident_context}\n\n"
            f"Execute the full response protocol: "
            f"analyze, propose containment, execute with approval, "
            f"and generate post-mortem."
        )}
    ]

    # Agentic loop: the agent decides when to stop
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=system_prompt,
            tools=incident_tools,
            messages=messages
        )

        # Process the response
        if response.stop_reason == "end_turn":
            # The agent has finished its analysis
            return extract_final_report(response, messages)

        if response.stop_reason == "tool_use":
            # Execute the requested tools
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })

            # Add agent response and results to history
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

import json
import time
import hashlib
import hmac

# Log of all actions for auditing
action_log: list[dict] = []

def execute_containment(action: dict, incident_id: str) -> dict:
    """Execute a containment action after human approval."""

    # Classify the action by risk level
    destructive_actions = {"isolate_container", "revoke_credentials",
                          "block_ip_range", "scale_down_service"}

    if action["type"] in destructive_actions:
        # Request human approval via Slack
        approval = send_slack_approval_request(
            channel="#incident-response",
            message=(
                f":rotating_light: *Proposed containment action*\n"
                f"Incident: `{incident_id}`\n"
                f"Action: {action['description']}\n"
                f"Impact: {action['impact']}\n"
                f"Rationale: {action['rationale']}\n\n"
                f"React :white_check_mark: to approve "
                f"or :x: to reject."
            ),
            timeout_seconds=300  # 5 minutes to respond
        )

        if not approval.get("approved"):
            log_action(incident_id, action, "rejected", approval.get("reason"))
            return {"status": "rejected", "reason": approval.get("reason")}

    # Execute the approved (or non-destructive) action
    result = _dispatch_action(action)

    # Record for auditing and post-mortem
    log_action(incident_id, action, "executed", json.dumps(result))

    return {"status": "executed", "result": result}

def log_action(incident_id: str, action: dict, status: str, detail: str):
    """Record each action for full traceability."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "incident_id": incident_id,
        "action_type": action["type"],
        "description": action["description"],
        "status": status,
        "detail": detail,
        "operator": action.get("approved_by", "system")
    }
    action_log.append(entry)

def generate_postmortem_draft(incident_id: str) -> str:
    """Generate a post-mortem draft using Claude."""

    # Gather all incident data
    incident_data = get_incident_data(incident_id)
    actions = [a for a in action_log if a["incident_id"] == incident_id]

    prompt = f"""Generate a structured post-mortem for the following incident.
Use the blameless format (no blame, focused on systems and processes).

## Incident data
- ID: {incident_data['incident_id']}
- Severity: {incident_data['severity']}
- Detected: {incident_data['detected_at']}
- Contained: {incident_data['contained_at']}
- Resolved: {incident_data['resolved_at']}

## Correlated alerts
{json.dumps(incident_data['alerts'], indent=2, default=str)}

## Executed actions
{json.dumps(actions, indent=2, default=str)}

## Affected services
{json.dumps(incident_data['affected_services'], indent=2)}

## Required structure
1. Executive summary (3-5 sentences)
2. Detailed timeline with timestamps
3. Root cause (5 Whys)
4. Impact (affected users, duration, compromised data)
5. What went well
6. What can be improved
7. Action items with owner and deadline
8. Metrics: MTTD, MTTC, MTTR

IMPORTANT: Do not invent data. If any information is not available
in the provided data, explicitly indicate "[PENDING: complete
with on-call team]"."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text
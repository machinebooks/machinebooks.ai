"""
PQC-Day and the Machine — Chapter 26
Pattern: Continuous cryptographic monitoring agent with Claude tool-calling

This is a didactic example from the book, not production code.
See chapter 26 for full context and explanation.

Requires: pip install anthropic
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

try:
    import anthropic
except ImportError:
    anthropic = None


# --- Tool definitions ---

TOOLS = [
    {
        "name": "check_repo_changes",
        "description": "Detect recent commits that modify files with cryptographic patterns",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_id": {"type": "integer"},
                "since": {"type": "string", "description": "ISO datetime"}
            },
            "required": ["repo_id", "since"]
        }
    },
    {
        "name": "check_certificate_renewals",
        "description": "Detect renewed or soon-to-expire certificates",
        "input_schema": {
            "type": "object",
            "properties": {
                "organization_id": {"type": "integer"}
            },
            "required": ["organization_id"]
        }
    },
    {
        "name": "check_cloud_config_drift",
        "description": "Detect changes in cryptographic configuration of cloud services",
        "input_schema": {
            "type": "object",
            "properties": {
                "cloud_account_id": {"type": "integer"}
            },
            "required": ["cloud_account_id"]
        }
    },
    {
        "name": "analyze_file",
        "description": "Analyze a specific file for cryptographic patterns",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_id": {"type": "integer"},
                "file_path": {"type": "string"}
            },
            "required": ["repo_id", "file_path"]
        }
    },
    {
        "name": "update_crypto_inventory",
        "description": "Update the cryptographic inventory with new findings",
        "input_schema": {
            "type": "object",
            "properties": {
                "finding": {"type": "object"},
                "action": {"type": "string", "enum": ["create", "update", "resolve"]}
            },
            "required": ["finding", "action"]
        }
    }
]

SYSTEM_PROMPT = """You are a continuous cryptographic monitoring agent.
Your goal is to detect changes in the organization's cryptographic assets
and update the post-quantum readiness inventory.

Priorities:
1. CRITICAL: New uses of quantum-vulnerable algorithms in production
2. HIGH: Certificates renewed with non-PQC-compliant algorithms
3. MEDIUM: Cloud config changes affecting encryption
4. LOW: Dependency updates with cryptographic implications

When you detect a change, analyze the impact, classify the severity,
and update the inventory. Do not generate alerts for irrelevant changes.
Be precise: a false positive erodes the team's trust."""


def execute_tool(tool_name: str, tool_input: dict) -> dict:
    """Execute a tool and return the result.

    In production, these would connect to real data sources.
    Here we return sample data for demonstration.
    """
    if tool_name == "check_repo_changes":
        return {
            "changes_found": 2,
            "commits": [
                {
                    "sha": "abc123",
                    "message": "Update authentication module",
                    "files_changed": ["auth/jwt_handler.py", "auth/crypto.py"],
                    "crypto_relevant": True
                },
                {
                    "sha": "def456",
                    "message": "Fix CSS styles",
                    "files_changed": ["static/styles.css"],
                    "crypto_relevant": False
                }
            ]
        }
    elif tool_name == "check_certificate_renewals":
        return {
            "certificates_checked": 5,
            "renewals": [
                {
                    "domain": "api.example.com",
                    "algorithm": "ECDSA-P256",
                    "expires_in_days": 15,
                    "pqc_compliant": False
                }
            ]
        }
    elif tool_name == "check_cloud_config_drift":
        return {
            "drift_detected": 1,
            "changes": [
                {
                    "resource": "KMS Key key-001",
                    "change": "Key rotation completed",
                    "algorithm": "RSA-2048",
                    "pqc_impact": "Key still uses quantum-vulnerable algorithm"
                }
            ]
        }
    elif tool_name == "analyze_file":
        return {
            "file": tool_input.get("file_path", "unknown"),
            "findings": [
                {
                    "algorithm": "RSA-2048",
                    "line": 45,
                    "severity": "critical",
                    "description": "RSA key generation for JWT signing"
                }
            ]
        }
    elif tool_name == "update_crypto_inventory":
        return {
            "status": "updated",
            "action": tool_input.get("action", "create"),
            "finding_id": 42
        }
    else:
        return {"error": f"Unknown tool: {tool_name}"}


def extract_summary(response) -> str:
    """Extract text summary from the final response."""
    for block in response.content:
        if hasattr(block, 'text'):
            return block.text[:500]
    return "Monitoring cycle completed"


def run_monitoring_cycle(
    organization_id: int,
    repos: List[int],
    cloud_accounts: List[int],
    last_check: Optional[str] = None
) -> dict:
    """Execute a complete monitoring cycle."""
    if not anthropic:
        return {"error": "anthropic package not installed"}

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        return {"error": "ANTHROPIC_API_KEY not set"}

    client = anthropic.Anthropic(api_key=api_key)

    since = last_check or (
        datetime.utcnow() - timedelta(hours=24)
    ).isoformat()

    initial_prompt = f"""
    Execute a monitoring cycle for organization {organization_id}.
    Last check: {since}
    Repositories to monitor: {repos}
    Cloud accounts to monitor: {cloud_accounts}

    Check for changes in repos, certificates, and cloud.
    Analyze only changes relevant to PQC readiness.
    Update the inventory with each new or modified finding.
    """

    messages = [{"role": "user", "content": initial_prompt}]
    findings = []
    max_iterations = 15

    for iteration in range(max_iterations):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages
        )

        # Process tool calls
        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    })
                    if block.name == "update_crypto_inventory":
                        findings.append(result)

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            # Agent has finished its cycle
            break

    return {
        "organization_id": organization_id,
        "cycle_completed": datetime.utcnow().isoformat(),
        "iterations": iteration + 1,
        "findings_updated": len(findings),
        "summary": extract_summary(response)
    }


# --- Main ---
if __name__ == '__main__':
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("Set ANTHROPIC_API_KEY to run the monitoring agent.")
        print("\nThis agent monitors:")
        print("  - Repository commits for cryptographic changes")
        print("  - Certificate renewals and PQC compliance")
        print("  - Cloud configuration drift")
        print("\nSee chapter 26 for the full explanation.")
    else:
        print("Starting monitoring cycle...\n")
        result = run_monitoring_cycle(
            organization_id=1,
            repos=[1, 2, 3],
            cloud_accounts=[1],
            last_check=None
        )

        print(f"Cycle completed: {result.get('cycle_completed')}")
        print(f"Iterations: {result.get('iterations')}")
        print(f"Findings updated: {result.get('findings_updated')}")
        print(f"\nSummary: {result.get('summary', 'N/A')}")

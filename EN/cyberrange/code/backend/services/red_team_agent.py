# Companion code for "The Cyber Range and the Machine" — Chapter 19
# Red team AI agent with MITRE ATT&CK technique selection and guardrails.
# This is STARTER code — not production-ready.
#
# Requires: pip install anthropic
#
# WARNING: This agent executes offensive security actions.
# Only run inside an isolated Cyber Range workzone with proper authorization.

import json
import os
import time
from dataclasses import dataclass, field

import anthropic

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "<YOUR_API_KEY>")
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# -- Guardrails (Chapter 19: critical safety controls) ---------------------

@dataclass
class AgentGuardrails:
    """
    Safety controls for the red team agent.

    Chapter 19 explains why every offensive AI agent needs:
    - Network scope restriction (only target the workzone)
    - Iteration limit (prevent infinite loops)
    - Kill switch (immediate stop capability)
    - Action logging (full audit trail)
    """
    allowed_networks: list[str] = field(default_factory=lambda: ["10.100.0.0/16"])
    max_iterations: int = 50
    kill_switch: bool = False
    current_iteration: int = 0
    action_log: list[dict] = field(default_factory=list)

    def check_target(self, target_ip: str) -> bool:
        """Verify target is within allowed network scope."""
        # Simplified check — use ipaddress module in production
        for network in self.allowed_networks:
            prefix = network.split("/")[0].rsplit(".", 1)[0]
            if target_ip.startswith(prefix):
                return True
        return False

    def check_iteration_limit(self) -> bool:
        """Return False if the agent has exceeded its iteration budget."""
        return self.current_iteration < self.max_iterations

    def log_action(self, tool: str, target: str, result: str) -> None:
        """Record every action for audit trail."""
        self.action_log.append({
            "iteration": self.current_iteration,
            "timestamp": time.time(),
            "tool": tool,
            "target": target,
            "result_summary": result[:500],
        })

    def activate_kill_switch(self) -> None:
        """Emergency stop — called by operator or automated safety check."""
        self.kill_switch = True


# -- Tool definitions for the red team agent -------------------------------

TOOLS = [
    {
        "name": "nmap_scan",
        "description": "Run an Nmap scan against a target. Returns open ports and services.",
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Target IP address"},
                "scan_type": {
                    "type": "string",
                    "enum": ["quick", "full", "vuln"],
                    "description": "Scan intensity: quick (top 100), full (all ports), vuln (scripts)",
                },
            },
            "required": ["target"],
        },
    },
    {
        "name": "exploit",
        "description": "Attempt to exploit a specific vulnerability on a target.",
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Target IP:port"},
                "cve": {"type": "string", "description": "CVE identifier (e.g. CVE-2021-44228)"},
                "technique": {"type": "string", "description": "MITRE ATT&CK technique ID"},
            },
            "required": ["target"],
        },
    },
    {
        "name": "lateral_move",
        "description": "Attempt lateral movement from a compromised host to another target.",
        "input_schema": {
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "Compromised host IP"},
                "target": {"type": "string", "description": "Next target IP"},
                "method": {
                    "type": "string",
                    "enum": ["ssh_key", "pass_the_hash", "smb_relay", "rdp"],
                    "description": "Lateral movement method",
                },
                "credentials": {"type": "string", "description": "Credentials to use (if any)"},
            },
            "required": ["source", "target", "method"],
        },
    },
]


# -- Tool handlers (stubs — in production, these call real tools) ----------

def handle_nmap_scan(target: str, scan_type: str = "quick") -> dict:
    """Stub: would execute nmap via subprocess in a real deployment."""
    return {
        "target": target,
        "scan_type": scan_type,
        "status": "simulated",
        "open_ports": [
            {"port": 22, "service": "ssh", "version": "OpenSSH 8.2"},
            {"port": 80, "service": "http", "version": "Apache 2.4.41"},
            {"port": 3306, "service": "mysql", "version": "MySQL 8.0"},
        ],
    }


def handle_exploit(target: str, cve: str = "", technique: str = "") -> dict:
    """Stub: would execute exploit framework commands in production."""
    return {
        "target": target,
        "cve": cve,
        "technique": technique,
        "status": "simulated",
        "success": True,
        "access_level": "user",
    }


def handle_lateral_move(source: str, target: str, method: str, **kwargs) -> dict:
    """Stub: would attempt real lateral movement in production."""
    return {
        "source": source,
        "target": target,
        "method": method,
        "status": "simulated",
        "success": True,
    }


TOOL_HANDLERS = {
    "nmap_scan": handle_nmap_scan,
    "exploit": handle_exploit,
    "lateral_move": handle_lateral_move,
}


# -- Main agent loop -------------------------------------------------------

def run_red_team_agent(
    objective: str,
    target_network: str,
    mitre_techniques: list[str] | None = None,
    guardrails: AgentGuardrails | None = None,
) -> dict:
    """
    Run the red team AI agent against a target network.

    Chapter 19: the agent autonomously:
    1. Scans the network to discover hosts and services
    2. Selects appropriate MITRE ATT&CK techniques
    3. Attempts exploitation and lateral movement
    4. Reports findings with technique mapping

    Args:
        objective: What the agent should try to achieve
        target_network: Target network CIDR (must be in guardrails scope)
        mitre_techniques: Optional list of ATT&CK techniques to prioritize
        guardrails: Safety controls (defaults created if not provided)

    Returns:
        Report dict with actions taken, findings, and MITRE mappings.
    """
    if guardrails is None:
        guardrails = AgentGuardrails(allowed_networks=[target_network])

    technique_context = ""
    if mitre_techniques:
        technique_context = f"\nPrioritize these MITRE ATT&CK techniques: {', '.join(mitre_techniques)}"

    system_prompt = (
        "You are a red team operator conducting an authorized penetration test "
        "inside an isolated Cyber Range workzone. Your objective is to test "
        "defenses by discovering and exploiting vulnerabilities.\n\n"
        "RULES:\n"
        f"- ONLY target hosts in {target_network}\n"
        "- Document every action with MITRE ATT&CK technique IDs\n"
        "- Stop if you achieve the objective or exhaust available techniques\n"
        "- Report all findings including failed attempts\n"
        f"{technique_context}"
    )

    messages = [{"role": "user", "content": f"Objective: {objective}"}]

    while guardrails.check_iteration_limit() and not guardrails.kill_switch:
        guardrails.current_iteration += 1

        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            # Agent finished — extract final report
            final_text = "".join(
                block.text for block in response.content if hasattr(block, "text")
            )
            return {
                "status": "completed",
                "iterations": guardrails.current_iteration,
                "report": final_text,
                "action_log": guardrails.action_log,
            }

        # Process tool calls with guardrail checks
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            target_ip = block.input.get("target", "").split(":")[0]

            # Guardrail: verify target is in scope
            if target_ip and not guardrails.check_target(target_ip):
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps({
                        "error": f"BLOCKED: {target_ip} is outside allowed scope"
                    }),
                })
                continue

            handler = TOOL_HANDLERS.get(block.name)
            if handler:
                result = handler(**block.input)
                guardrails.log_action(block.name, target_ip, str(result))
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    # Reached limit or kill switch activated
    return {
        "status": "stopped",
        "reason": "kill_switch" if guardrails.kill_switch else "iteration_limit",
        "iterations": guardrails.current_iteration,
        "action_log": guardrails.action_log,
    }

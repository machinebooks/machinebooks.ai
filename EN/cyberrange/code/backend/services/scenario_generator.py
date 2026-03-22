# Companion code for "The Cyber Range and the Machine" — Chapter 17
# Claude Agent SDK scenario generation from natural language.
# This is STARTER code — not production-ready.
#
# Requires: pip install anthropic

import json
import os

import anthropic

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "<YOUR_API_KEY>")
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# -- Tool definitions for the scenario generation agent --------------------
# Chapter 17: the agent has tools to query available templates,
# validate network topologies, and generate Ansible playbooks.

TOOLS = [
    {
        "name": "list_templates",
        "description": (
            "List available VM templates in Proxmox. Returns template IDs, "
            "names, and OS types."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "os_filter": {
                    "type": "string",
                    "description": "Filter by OS: 'linux', 'windows', or 'all'",
                }
            },
            "required": [],
        },
    },
    {
        "name": "validate_network",
        "description": (
            "Validate a network topology definition. Checks for IP conflicts, "
            "VLAN availability, and routing rules."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topology": {
                    "type": "object",
                    "description": "Network topology as JSON with nodes and links",
                }
            },
            "required": ["topology"],
        },
    },
    {
        "name": "generate_playbook",
        "description": (
            "Generate an Ansible playbook for provisioning a vulnerable VM "
            "based on specified CVEs or MITRE ATT&CK techniques."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "os": {"type": "string", "description": "Target OS: ubuntu, centos, windows"},
                "vulnerabilities": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of CVE IDs or vulnerability descriptions",
                },
                "mitre_techniques": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "MITRE ATT&CK technique IDs (e.g. T1021.001)",
                },
            },
            "required": ["os", "vulnerabilities"],
        },
    },
]


# -- Tool handlers (simplified stubs) -------------------------------------

def handle_list_templates(os_filter: str = "all") -> list[dict]:
    """Stub: in production, calls proxmox_service.list_templates()."""
    # Chapter 10: these come from the Proxmox API
    templates = [
        {"vmid": 9000, "name": "ubuntu-22.04-base", "os": "linux"},
        {"vmid": 9001, "name": "ubuntu-20.04-base", "os": "linux"},
        {"vmid": 9010, "name": "windows-server-2022", "os": "windows"},
        {"vmid": 9011, "name": "windows-10-base", "os": "windows"},
        {"vmid": 9020, "name": "centos-8-base", "os": "linux"},
        {"vmid": 9030, "name": "kali-2024-attacker", "os": "linux"},
    ]
    if os_filter != "all":
        templates = [t for t in templates if t["os"] == os_filter]
    return templates


def handle_validate_network(topology: dict) -> dict:
    """Stub: validate network topology for conflicts."""
    nodes = topology.get("nodes", [])
    errors = []
    ips_seen = set()
    for node in nodes:
        ip = node.get("ip")
        if ip in ips_seen:
            errors.append(f"Duplicate IP: {ip}")
        ips_seen.add(ip)
    return {"valid": len(errors) == 0, "errors": errors}


def handle_generate_playbook(os: str, vulnerabilities: list, **kwargs) -> str:
    """Stub: returns a basic playbook skeleton."""
    return f"# Auto-generated playbook for {os}\n# Vulns: {vulnerabilities}\n---\n"


TOOL_HANDLERS = {
    "list_templates": handle_list_templates,
    "validate_network": handle_validate_network,
    "generate_playbook": handle_generate_playbook,
}


# -- Main generation function (agentic loop) --------------------------------

def generate_scenario(description: str, difficulty: str = "medium") -> dict:
    """
    Generate a complete exercise scenario from a natural language description.

    Chapter 17: the agent loop:
    1. Claude analyzes the request
    2. Uses tools to query templates and validate topology
    3. Produces a structured scenario definition
    4. We validate the output before returning

    Args:
        description: Natural language scenario request, e.g.
            "Create a web exploitation exercise with SQL injection
             and privilege escalation on Ubuntu"
        difficulty: easy, medium, hard, or insane

    Returns:
        Structured scenario dict with topology, playbooks, and flags.
    """
    system_prompt = (
        "You are a Cyber Range scenario architect. Generate exercise scenarios "
        "based on user descriptions. Use the available tools to check templates "
        "and validate network topologies. Output a structured JSON scenario.\n\n"
        f"Target difficulty: {difficulty}\n"
        "Always include: network topology, VM assignments, vulnerability list, "
        "MITRE ATT&CK mapping, and estimated duration."
    )

    messages = [{"role": "user", "content": description}]

    # Agentic loop: keep calling Claude until it stops requesting tools
    for _iteration in range(10):  # Safety limit
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,
        )

        # Check if Claude wants to use a tool
        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    handler = TOOL_HANDLERS.get(block.name)
                    if handler:
                        result = handler(**block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result),
                        })

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
            continue

        # Claude finished — extract the final text response
        final_text = "".join(
            block.text for block in response.content if hasattr(block, "text")
        )

        # Try to parse as JSON scenario
        try:
            scenario = json.loads(final_text)
        except json.JSONDecodeError:
            scenario = {"raw_response": final_text, "parsed": False}

        return scenario

    return {"error": "Agent exceeded maximum iterations"}

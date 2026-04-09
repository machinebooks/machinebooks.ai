# Extracted from: LibroAISafety/ch-22-secure-architecture.md
from typing import Any
from dataclasses import dataclass, field

@dataclass
class ToolPermission:
    """Defines the permissions of a tool for a given context."""
    tool_name: str
    allowed_actions: list[str]
    max_calls_per_session: int = 10
    requires_user_confirmation: bool = False
    allowed_parameters: dict[str, Any] = field(default_factory=dict)

# Example: permissions profile for a cost query agent
COST_AGENT_PERMISSIONS = [
    ToolPermission(
        tool_name="query_database",
        allowed_actions=["SELECT"],    # read-only, never UPDATE/DELETE
        max_calls_per_session=20,
        allowed_parameters={"tables": ["costs", "budgets", "usage"]},
    ),
    ToolPermission(
        tool_name="send_alert",
        allowed_actions=["email"],
        max_calls_per_session=3,       # maximum 3 alerts per session
        requires_user_confirmation=True,  # requires human approval
    ),
    ToolPermission(
        tool_name="modify_budget",
        allowed_actions=[],            # disabled -- read-only
        max_calls_per_session=0,
    ),
]

def validate_tool_call(
    tool_name: str,
    action: str,
    params: dict,
    permissions: list[ToolPermission],
    session_calls: dict[str, int],
) -> bool:
    """
    Validates that a tool call complies with defined permissions.
    Returns False if the call should be blocked.
    """
    perm = next((p for p in permissions if p.tool_name == tool_name), None)
    if perm is None:
        return False  # unauthorized tool

    if action not in perm.allowed_actions:
        return False  # action not allowed

    calls = session_calls.get(tool_name, 0)
    if calls >= perm.max_calls_per_session:
        return False  # call limit exceeded

    # Validate parameters if restrictions are defined
    for key, allowed_values in perm.allowed_parameters.items():
        if key in params and params[key] not in allowed_values:
            return False  # parameter outside allowed range

    return True

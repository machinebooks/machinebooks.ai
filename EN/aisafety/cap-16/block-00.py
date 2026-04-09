# Extracted from: LibroAISafety/ch-16-agent-security.md
from dataclasses import dataclass, field
from typing import Any, Callable
from enum import Enum
import re
import logging

logger = logging.getLogger("agent_security")

class RiskLevel(Enum):
    LOW = "low"           # Data reading, queries
    MEDIUM = "medium"     # Modification of own data
    HIGH = "high"         # Deletion, external sending
    CRITICAL = "critical" # Irreversible actions in production

@dataclass
class ToolPermission:
    """Defines what a tool can do and under what conditions."""
    name: str
    risk_level: RiskLevel
    allowed_params: dict[str, type]      # Allowed parameters and their types
    forbidden_patterns: list[str] = field(default_factory=list)
    requires_approval: bool = False       # True = human-in-the-loop
    max_calls_per_session: int = 100      # Rate limiting per session

class ToolValidator:
    """Validates tool invocations before executing them."""

    def __init__(self, permissions: list[ToolPermission]):
        self._permissions = {p.name: p for p in permissions}
        self._call_counts: dict[str, int] = {}

    def validate(self, tool_name: str, params: dict[str, Any]) -> tuple[bool, str]:
        """Returns (allowed, reason) for each invocation."""
        perm = self._permissions.get(tool_name)
        if not perm:
            logger.warning(f"Unregistered tool: {tool_name}")
            return False, f"Tool '{tool_name}' is not in the registry"

        # Validate parameter types
        for key, value in params.items():
            expected_type = perm.allowed_params.get(key)
            if expected_type is None:
                return False, f"Parameter '{key}' not allowed"
            if not isinstance(value, expected_type):
                return False, f"Incorrect type for '{key}'"

        # Detect forbidden patterns (SQL injection, shell commands, etc.)
        param_str = str(params)
        for pattern in perm.forbidden_patterns:
            if re.search(pattern, param_str, re.IGNORECASE):
                logger.critical(
                    f"Forbidden pattern detected in {tool_name}: {pattern}"
                )
                return False, f"Prohibited content detected"

        # Rate limiting
        count = self._call_counts.get(tool_name, 0)
        if count >= perm.max_calls_per_session:
            return False, f"Invocation limit reached ({count})"
        self._call_counts[tool_name] = count + 1

        # Human approval for high-risk tools
        if perm.requires_approval:
            return False, "REQUIRES_APPROVAL"

        return True, "OK"

# Extracted from: LibroAISafety/ch-16-agent-security.md
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum

class ToolScope(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"

@dataclass
class AgentPermissionGrant:
    """Temporary permission grant for an agent."""
    agent_id: str
    tool_name: str
    scopes: list[ToolScope]
    granted_at: datetime
    expires_at: datetime
    granted_by: str          # ID of the user or system granting
    reason: str              # Access justification
    max_invocations: int = 100  # Usage limit

    def is_valid(self) -> bool:
        """Checks if the permission is still active."""
        now = datetime.now(timezone.utc)
        return now < self.expires_at

    def allows(self, scope: ToolScope) -> bool:
        """Checks if the permission covers an operation."""
        return self.is_valid() and scope in self.scopes

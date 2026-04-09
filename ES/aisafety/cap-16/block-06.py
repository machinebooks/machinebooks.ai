# Extraido de: LibroAISafety/cap-16-seguridad-agentes.md
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
    """Concesión de permisos temporales para un agente."""
    agent_id: str
    tool_name: str
    scopes: list[ToolScope]
    granted_at: datetime
    expires_at: datetime
    granted_by: str          # ID del usuario o sistema que concede
    reason: str              # Justificación del acceso
    max_invocations: int = 100  # Límite de usos

    def is_valid(self) -> bool:
        """Verifica si el permiso sigue vigente."""
        now = datetime.now(timezone.utc)
        return now < self.expires_at

    def allows(self, scope: ToolScope) -> bool:
        """Verifica si el permiso cubre una operación."""
        return self.is_valid() and scope in self.scopes

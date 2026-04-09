# Extraido de: LibroAISafety/cap-17-mcp-seguridad.md
from dataclasses import dataclass, field
from enum import Enum

class DataClassification(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

@dataclass
class ServerPolicy:
    """Política de seguridad para un servidor MCP."""
    server_id: str
    data_classification: DataClassification
    # Servidores a los que puede fluir datos de este servidor
    allowed_targets: list[str] = field(default_factory=list)
    # Herramientas bloqueadas para este servidor
    blocked_tools: list[str] = field(default_factory=list)

class MCPIsolationProxy:
    """Proxy que aísla contextos entre servidores MCP."""

    def __init__(self):
        self._policies: dict[str, ServerPolicy] = {}
        # Rastrea de qué servidor proviene cada dato en el contexto
        self._data_provenance: dict[str, str] = {}

    def register_server(self, policy: ServerPolicy):
        """Registra un servidor con su política de aislamiento."""
        self._policies[policy.server_id] = policy

    def can_flow(self, source_server: str,
                 target_server: str) -> tuple[bool, str]:
        """Verifica si los datos pueden fluir de un servidor a otro."""
        source_policy = self._policies.get(source_server)
        target_policy = self._policies.get(target_server)

        if not source_policy or not target_policy:
            return False, "Servidor no registrado"

        # Los datos restringidos no fluyen a ningún servidor externo
        if (source_policy.data_classification
                == DataClassification.RESTRICTED):
            return False, "Datos RESTRICTED no pueden fluir externamente"

        # Verificar lista de destinos permitidos
        if target_server not in source_policy.allowed_targets:
            return False, (f"Flujo {source_server} → {target_server}"
                           " no autorizado")

        # Los datos confidenciales no fluyen a servidores con
        # clasificación inferior
        if (source_policy.data_classification
                == DataClassification.CONFIDENTIAL
                and target_policy.data_classification
                == DataClassification.PUBLIC):
            return False, "Datos CONFIDENTIAL no fluyen a servidor PUBLIC"

        return True, "Flujo autorizado"

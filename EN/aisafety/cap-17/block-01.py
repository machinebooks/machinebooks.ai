# Extracted from: LibroAISafety/ch-17-mcp-security.md
from dataclasses import dataclass, field
from enum import Enum

class DataClassification(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

@dataclass
class ServerPolicy:
    """Security policy for an MCP server."""
    server_id: str
    data_classification: DataClassification
    # Servers to which data from this server can flow
    allowed_targets: list[str] = field(default_factory=list)
    # Blocked tools for this server
    blocked_tools: list[str] = field(default_factory=list)

class MCPIsolationProxy:
    """Proxy that isolates contexts between MCP servers."""

    def __init__(self):
        self._policies: dict[str, ServerPolicy] = {}
        # Tracks which server each datum in the context comes from
        self._data_provenance: dict[str, str] = {}

    def register_server(self, policy: ServerPolicy):
        """Registers a server with its isolation policy."""
        self._policies[policy.server_id] = policy

    def can_flow(self, source_server: str,
                 target_server: str) -> tuple[bool, str]:
        """Checks whether data can flow from one server to another."""
        source_policy = self._policies.get(source_server)
        target_policy = self._policies.get(target_server)

        if not source_policy or not target_policy:
            return False, "Unregistered server"

        # RESTRICTED data does not flow to any external server
        if (source_policy.data_classification
                == DataClassification.RESTRICTED):
            return False, "RESTRICTED data cannot flow externally"

        # Check allowed destinations list
        if target_server not in source_policy.allowed_targets:
            return False, (f"Flow {source_server} -> {target_server}"
                           " not authorized")

        # CONFIDENTIAL data does not flow to servers with
        # lower classification
        if (source_policy.data_classification
                == DataClassification.CONFIDENTIAL
                and target_policy.data_classification
                == DataClassification.PUBLIC):
            return False, "CONFIDENTIAL data does not flow to PUBLIC server"

        return True, "Flow authorized"

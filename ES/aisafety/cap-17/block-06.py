# Extraido de: LibroAISafety/cap-17-mcp-seguridad.md
import hashlib
import json
from datetime import datetime, timezone

class MCPAuditChain:
    """Log de auditoría MCP con hash encadenado."""

    def __init__(self, server_id: str):
        self.server_id = server_id
        self._prev_hash = "0" * 64  # Genesis hash

    def log(self, event_type: str, tool: str, params_hash: str,
            result_status: str) -> dict:
        entry = {
            "server": self.server_id,
            "ts": datetime.now(timezone.utc).isoformat(),
            "type": event_type,
            "tool": tool,
            "params_hash": params_hash,
            "status": result_status,
            "prev_hash": self._prev_hash,
        }
        entry_bytes = json.dumps(entry, sort_keys=True).encode()
        entry["hash"] = hashlib.sha256(entry_bytes).hexdigest()
        self._prev_hash = entry["hash"]
        return entry

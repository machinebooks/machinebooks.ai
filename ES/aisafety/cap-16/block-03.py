# Extraido de: LibroAISafety/cap-16-seguridad-agentes.md
import json
import hashlib
from datetime import datetime, timezone

class AgentAuditLog:
    """Registro inmutable de toda la actividad del agente."""

    def __init__(self, agent_id: str, storage_backend):
        self.agent_id = agent_id
        self.storage = storage_backend
        self._sequence = 0

    def log_event(self, event_type: str, data: dict) -> str:
        """Registra un evento con hash encadenado para integridad."""
        self._sequence += 1
        event = {
            "agent_id": self.agent_id,
            "sequence": self._sequence,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": event_type,  # tool_call, tool_response, decision, alert
            "data": data,
        }
        # Hash encadenado: cada evento incluye el hash del anterior
        event_json = json.dumps(event, sort_keys=True)
        event["hash"] = hashlib.sha256(event_json.encode()).hexdigest()
        self.storage.append(event)
        return event["hash"]

    def log_tool_call(self, tool_name: str, params: dict,
                      validation_result: str):
        """Atajo para registrar invocaciones de herramientas."""
        return self.log_event("tool_call", {
            "tool": tool_name,
            "params": params,
            "validation": validation_result,
        })

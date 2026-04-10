# Extracted from: LibroAISafety/ch-16-agent-security.md
import json
import hashlib
from datetime import datetime, timezone

class AgentAuditLog:
    """Immutable log of all agent activity."""

    def __init__(self, agent_id: str, storage_backend):
        self.agent_id = agent_id
        self.storage = storage_backend
        self._sequence = 0

    def log_event(self, event_type: str, data: dict) -> str:
        """Logs an event with chained hash for integrity."""
        self._sequence += 1
        event = {
            "agent_id": self.agent_id,
            "sequence": self._sequence,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": event_type,  # tool_call, tool_response, decision, alert
            "data": data,
        }
        # Chained hash: each event includes the hash of the previous one
        event_json = json.dumps(event, sort_keys=True)
        event["hash"] = hashlib.sha256(event_json.encode()).hexdigest()
        self.storage.append(event)
        return event["hash"]

    def log_tool_call(self, tool_name: str, params: dict,
                      validation_result: str):
        """Shortcut for logging tool invocations."""
        return self.log_event("tool_call", {
            "tool": tool_name,
            "params": params,
            "validation": validation_result,
        })

# Extracted from: LibroAISafety/ch-17-mcp-security.md
import json
from datetime import datetime, timezone

class MCPSessionAuditor:
    """Logs security events of a complete MCP session."""

    def __init__(self, session_id: str, server_id: str):
        self.session_id = session_id
        self.server_id = server_id
        self._events: list[dict] = []

    def log_discovery(self, tools: list[dict],
                      validated_tools: list[dict]):
        """Logs tool discovery and validation."""
        removed = [t["name"] for t in tools
                   if t not in validated_tools]
        self._append_event("discovery", {
            "total_tools": len(tools),
            "validated_tools": len(validated_tools),
            "removed_tools": removed,
        })

    def log_tool_call(self, tool_name: str, params_hash: str,
                      result_status: str, duration_ms: float):
        """Logs a tool invocation."""
        self._append_event("tool_call", {
            "tool": tool_name,
            "params_hash": params_hash,
            "status": result_status,
            "duration_ms": round(duration_ms, 2),
        })

    def log_security_event(self, event_type: str,
                           details: str):
        """Logs a security event (injection, block)."""
        self._append_event("security", {
            "type": event_type,
            "details": details,
        })

    def _append_event(self, category: str, data: dict):
        self._events.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "server_id": self.server_id,
            "category": category,
            "data": data,
        })

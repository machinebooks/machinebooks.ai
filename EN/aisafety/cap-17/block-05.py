# Extracted from: LibroAISafety/ch-17-mcp-security.md
import time
from collections import defaultdict

class ToolRateLimiter:
    """Rate limiting per tool and per session."""

    def __init__(self, default_rpm: int = 30):
        self._limits: dict[str, int] = {}  # tool_name -> max RPM
        self._calls: dict[str, list[float]] = defaultdict(list)
        self._default_rpm = default_rpm

    def set_limit(self, tool_name: str, max_rpm: int):
        self._limits[tool_name] = max_rpm

    def allow(self, tool_name: str, session_id: str) -> bool:
        """Returns True if the invocation is within the limit."""
        key = f"{session_id}:{tool_name}"
        now = time.monotonic()
        limit = self._limits.get(tool_name, self._default_rpm)
        # Clean calls from more than 60 seconds ago
        self._calls[key] = [t for t in self._calls[key] if now - t < 60]
        if len(self._calls[key]) >= limit:
            return False
        self._calls[key].append(now)
        return True

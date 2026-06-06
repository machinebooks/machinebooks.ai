# Extracted from: LibroAIGateway/cap-21-audit-append-only.md
class AuditBatcher:
    def __init__(
        self,
        flush_interval_s: float = 1.0,    # flush every 1s
        max_batch: int = 100,              # or every 100 items
        queue_maxsize: int = 10_000,       # bounded queue
    ):
        self._queue = asyncio.Queue(maxsize=queue_maxsize)

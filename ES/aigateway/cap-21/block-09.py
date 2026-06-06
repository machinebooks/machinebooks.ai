# Extraído de: LibroAIGateway/cap-21-audit-append-only.md
async def enqueue(self, audit_payload: dict) -> bool:
    try:
        self._queue.put_nowait(audit_payload)
    except asyncio.QueueFull:
        metrics_service.AUDIT_BATCH_DROPPED_TOTAL.inc()
        return False
    return True

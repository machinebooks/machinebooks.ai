# Extracted from: LibroAIGateway/cap-20-classification-guardrails-firewall.md
# gateway/app/services/guardrail_service.py:77-88

async def _check_remote_invalidation() -> float:
    """Reads the timestamp of the last invalidate in Redis."""
    try:
        from app.core.redis_client import get_redis
        r = await get_redis()
        raw = await r.get(_REDIS_INVALIDATE_KEY)
        if raw is None:
            return 0.0
        return float(raw)
    except Exception:
        return 0.0

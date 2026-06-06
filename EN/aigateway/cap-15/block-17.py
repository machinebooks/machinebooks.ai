# Extracted from: LibroAIGateway/cap-15-rate-limiting.md
try:
    redis = await get_redis()
    key = f"sess_iter:{session_id}"
    current = await redis.eval(_INCR_WITH_TTL_SCRIPT, 1, key, str(ttl))
except Exception as exc:
    logger.debug("max_iterations:redis_failed err=%s", exc)
    return 0  # fail-open

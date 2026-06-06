# Extraído de: LibroAIGateway/cap-15-rate-limiting.md
if int(count) > rl.max_parallel:
    await redis.decr(key_par)           # deshace el propio INCR
    await _release_acquired(redis, acquired)  # libera los anteriores
    raise RateLimitExceeded(...)

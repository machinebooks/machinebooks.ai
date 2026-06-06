# Extracted from: LibroAIGateway/cap-15-rate-limiting.md
if int(count) > rl.max_parallel:
    await redis.decr(key_par)           # undoes its own INCR
    await _release_acquired(redis, acquired)  # releases the previous ones
    raise RateLimitExceeded(...)

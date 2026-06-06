# Extracted from: LibroAIGateway/cap-15-rate-limiting.md
if count == 1:
    # Safety TTL in case the DECR in finally is not called
    # (dead worker): after 10 min the gauge resets itself.
    await redis.expire(key_par, 600)

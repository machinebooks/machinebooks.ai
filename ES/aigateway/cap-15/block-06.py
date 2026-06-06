# Extraído de: LibroAIGateway/cap-15-rate-limiting.md
if count == 1:
    # TTL de seguridad por si el DECR del finally no se llama
    # (worker muerto): a los 10 min el gauge se reinicia solo.
    await redis.expire(key_par, 600)

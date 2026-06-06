# Extraído de: LibroAIGateway/cap-15-rate-limiting.md
# Intentar restar atómicamente
new_value = await redis.decrby(bucket_key, estimated_tokens)
if new_value >= 0:
    return True  # Reservó con éxito

# No había suficientes — devolver lo que tomamos prestado y esperar
await redis.incrby(bucket_key, estimated_tokens)
await asyncio.sleep(min(2.0, sleep_s))  # recheck cada 2s

# Extraído de: LibroAIGateway/cap-15-rate-limiting.md
# Refill perezoso: solo si han pasado >= 60s desde la última recarga
last_refill_str = await redis.get(refill_key)
last_refill = float(last_refill_str) if last_refill_str else 0.0
now = time.time()
if (now - last_refill) >= BUCKET_REFILL_INTERVAL_S:
    pipe = redis.pipeline()
    pipe.set(bucket_key, tpm_quota)
    pipe.set(refill_key, now)
    pipe.expire(bucket_key, 86_400)
    pipe.expire(refill_key, 86_400)
    await pipe.execute()

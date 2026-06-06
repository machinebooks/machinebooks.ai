# Extraído de: LibroAIGateway/cap-13-tenants-cuotas.md
# Throttle: 1 email cada 3600s por user+bucket
redis = await get_redis()
key = f"quota_alert:sent:{user_id}:{bucket}"
already = await redis.set(key, "1", ex=3600, nx=True)
if not already:
    return 0  # Ya se envió esta hora → no repetir

# Extracted from: LibroAIGateway/cap-13-tenants-quotas.md
# Throttle: 1 email every 3600s per user+bucket
redis = await get_redis()
key = f"quota_alert:sent:{user_id}:{bucket}"
already = await redis.set(key, "1", ex=3600, nx=True)
if not already:
    return 0  # Already sent this hour → do not repeat

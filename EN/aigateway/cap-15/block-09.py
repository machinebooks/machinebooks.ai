# Extracted from: LibroAIGateway/cap-15-rate-limiting.md
# Try to subtract atomically
new_value = await redis.decrby(bucket_key, estimated_tokens)
if new_value >= 0:
    return True  # Reserved successfully

# There were not enough — give back what we borrowed and wait
await redis.incrby(bucket_key, estimated_tokens)
await asyncio.sleep(min(2.0, sleep_s))  # recheck every 2s

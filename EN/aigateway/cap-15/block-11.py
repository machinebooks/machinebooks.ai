# Extracted from: LibroAIGateway/cap-15-rate-limiting.md
@classmethod
async def release(cls, deployment_id: int, tokens: int) -> None:
    """Returns tokens to the bucket (when the call was cancelled without using them)."""
    redis = await get_redis()
    await redis.incrby(f"{BUCKET_KEY_PREFIX}:{deployment_id}", tokens)

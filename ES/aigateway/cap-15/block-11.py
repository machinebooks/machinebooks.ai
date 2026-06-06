# Extraído de: LibroAIGateway/cap-15-rate-limiting.md
@classmethod
async def release(cls, deployment_id: int, tokens: int) -> None:
    """Devuelve tokens al bucket (cuando la llamada se canceló sin usarlos)."""
    redis = await get_redis()
    await redis.incrby(f"{BUCKET_KEY_PREFIX}:{deployment_id}", tokens)

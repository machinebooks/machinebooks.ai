# Extraído de: LibroAIGateway/cap-09-compresion-tokens.md
# gateway/app/services/semantic_dedup_service.py:228-234
def _semantic_redis_key(semantic_hash: str, *, user_id: int | str, purpose: str) -> str:
    """Key Redis scoped por user_id y purpose.
    Aunque el hash colisione entre users, la key es distinta → no leak posible."""
    return f"chat:semantic:{user_id}:{purpose.strip()}:{semantic_hash}"

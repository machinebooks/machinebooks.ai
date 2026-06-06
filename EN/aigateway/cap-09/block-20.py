# Extracted from: LibroAIGateway/cap-09-compression-tokens.md
# gateway/app/services/semantic_dedup_service.py:228-234
def _semantic_redis_key(semantic_hash: str, *, user_id: int | str, purpose: str) -> str:
    """Redis key scoped by user_id and purpose.
    Even if the hash collides across users, the key is different → no possible leak."""
    return f"chat:semantic:{user_id}:{purpose.strip()}:{semantic_hash}"

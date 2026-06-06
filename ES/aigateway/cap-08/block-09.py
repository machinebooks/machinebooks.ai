# Extraído de: LibroAIGateway/cap-08-caching.md
# gateway/app/services/semantic_cache_service.py:246-254
async def evict_older_than(db, days: int) -> int:
    cutoff = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        delete(SemanticCacheEntry).where(
            SemanticCacheEntry.last_used < cutoff
        )
    )
    await db.commit()
    return result.rowcount or 0

# Extracted from: LibroAIGateway/cap-19-threat-jailbreak-dlp-pii.md
# DB pattern loading with Redis cache (dlp_service.py:127-161)
async def _load_db_patterns(db: AsyncSession) -> list[dict]:
    try:
        redis = await get_redis()
        cached = await redis.get("n7x:dlp:db_patterns")
        if cached:
            return json.loads(cached)              # hit: 60s TTL
    except Exception:
        logger.warning("dlp:cache_read_failed")
    
    # Fallback direct DB query
    result = await db.execute(
        select(ContentFilter).where(
            ContentFilter.is_active == True,
            ContentFilter.filter_type.like("dlp_%"),
        )
    )

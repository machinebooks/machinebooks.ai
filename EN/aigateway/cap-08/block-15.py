# Extracted from: LibroAIGateway/cap-08-caching.md
# gateway/app/services/cache_service.py:357-377
async def get_cache_stats(redis) -> dict:
    total_sets = int(await redis.get("chat:cache:total_sets") or 0)
    total_hits = int(await redis.get("chat:cache:total_hits") or 0)
    hit_rate = round((total_hits / total_sets * 100) if total_sets > 0 else 0, 1)
    return {
        "total_sets": total_sets,
        "total_hits": total_hits,
        "hit_rate_pct": hit_rate,
    }

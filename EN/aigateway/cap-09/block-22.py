# Extracted from: LibroAIGateway/cap-09-compression-tokens.md
# gateway/app/services/semantic_dedup_service.py:295-306 (synthesized)
async def get_dedup_stats(redis) -> dict:
    total_sets = int(await redis.get("chat:semantic:total_sets") or 0)
    total_hits = int(await redis.get("chat:semantic:total_hits") or 0)
    hit_rate = round((total_hits / total_sets * 100) if total_sets > 0 else 0, 1)
    return {
        "semantic_dedup_total_stored": total_sets,
        "semantic_dedup_total_hits": total_hits,
        "semantic_dedup_hit_rate_pct": hit_rate,
    }

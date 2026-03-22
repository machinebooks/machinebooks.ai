# Extraído de: LibroCISO/cap-27-executive-dashboard.md
import json
from redis import Redis

CACHE_KEY = "exec_dashboard:{corporate_id}"
CACHE_TTL = 300  # 5 minutos

async def get_dashboard_cached(
    db: AsyncSession,
    corporate_id: int,
    redis: Redis,
) -> dict:
    """Dashboard con caché en Redis."""
    key = CACHE_KEY.format(corporate_id=corporate_id)
    cached = redis.get(key)
    if cached:
        return json.loads(cached)

    svc = ExecutiveDashboardService(db, corporate_id)
    data = await svc.get_dashboard()
    redis.setex(key, CACHE_TTL, json.dumps(data))
    return data

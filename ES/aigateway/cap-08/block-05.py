# Extraído de: LibroAIGateway/cap-08-caching.md
# gateway/app/services/dual_cache.py:82-169 (sintetizado)
class DualCache:
    async def get(self, key: str) -> Any | None:
        # 1. In-memory primero (hit = microsegundos)
        local = await self.in_memory.get(key)
        if local is not None:
            return local
        # 2. Redis como fallback (hit = milisegundos)
        raw = await self.redis.get(key)
        if raw is not None:
            await self.in_memory.set(key, raw, ttl=5)  # repobla L1
            return raw
        return None

    async def set(self, key: str, value: Any, redis_ttl: int | None = None):
        # Escribe a ambos niveles con TTLs distintos
        await self.in_memory.set(key, value, ttl=5)       # L1: 5s
        await self.redis.setex(key, redis_ttl or 300, value)  # L2: 5min

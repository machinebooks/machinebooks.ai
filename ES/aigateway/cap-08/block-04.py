# Extraído de: LibroAIGateway/cap-08-caching.md
# gateway/app/services/dual_cache.py:33-79 (sintetizado)
class InMemoryCache:
    def __init__(self, max_entries: int = 2048, default_ttl: int = 5):
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self._max_entries = max_entries
        self._default_ttl = default_ttl
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if expires_at < time.time():
            self._store.pop(key, None)  # limpieza diferida de expirados
            return None
        self._store.move_to_end(key)  # touch para LRU
        return value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        async with self._lock:
            self._store[key] = (time.time() + (ttl or self._default_ttl), value)
            self._store.move_to_end(key)
            while len(self._store) > self._max_entries:
                self._store.popitem(last=False)  # evict LRU más antiguo

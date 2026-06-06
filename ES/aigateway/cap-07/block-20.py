# Extraído de: LibroAIGateway/cap-07-adapters.md
def get_or_create(provider: str, key: str, factory):
    cache = _CLIENT_CACHES[provider]
    if key in cache:
        cache.move_to_end(key)
        return cache[key]
    client = factory()
    cache[key] = client
    if len(cache) > 16:
        evicted = cache.popitem(last=False)
        _close_client(evicted[1])  # best-effort
    return client

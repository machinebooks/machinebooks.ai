# Extraído de: LibroCyberrange/cap-15-ataques-defensa.md
# cyber-range-builder/backend/services/event_bus.py
_subs: dict[str, list[asyncio.Queue]] = defaultdict(list)

async def publish(topic: str, payload: str):
    """Publica un mensaje en todas las colas suscritas al topic."""
    for q in _subs.get(topic, []):
        await q.put(payload)

async def subscribe(topic: str):
    """Generador asíncrono: yield cada mensaje del topic."""
    q: asyncio.Queue[str] = asyncio.Queue()
    _subs[topic].append(q)
    try:
        while True:
            data = await q.get()
            yield data
    finally:
        _subs[topic].remove(q)

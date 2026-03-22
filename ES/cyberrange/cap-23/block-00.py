# Extraído de: LibroCyberrange/cap-23-tiempo-real-websocket.md
# Ejemplo didáctico: services/event_bus.py
"""Bus de eventos ligero basado en asyncio.Queue"""
import asyncio
from collections import defaultdict
from typing import Dict, List

# Diccionario de suscriptores por topic
_subs: Dict[str, List[asyncio.Queue]] = defaultdict(list)


async def publish(topic: str, payload: str):
    """Publicar un mensaje a todos los suscriptores de un topic"""
    for q in _subs.get(topic, []):
        await q.put(payload)


async def subscribe(topic: str):
    """
    Generador asíncrono que yield cada mensaje publicado
    en el topic dado. Se limpia automáticamente al salir.
    """
    q: asyncio.Queue[str] = asyncio.Queue()
    _subs[topic].append(q)
    try:
        while True:
            data = await q.get()
            yield data
    finally:
        _subs[topic].remove(q)

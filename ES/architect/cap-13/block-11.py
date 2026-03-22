# Extraído de: LibroTecnico/cap-13-busqueda-meilisearch.md
# Ejemplo didáctico: patrones/search/intent_patterns_db.py
# Carga de patrones desde base de datos con caché

from functools import lru_cache
import redis
import json

CACHE_KEY = "intent_patterns:v1"
CACHE_TTL = 300  # 5 minutos

def get_patterns_from_db() -> dict[str, list[str]]:
    """Carga patrones de clasificación desde BD con caché Redis."""
    r = redis.Redis()
    cached = r.get(CACHE_KEY)
    if cached:
        return json.loads(cached)

    # Consulta a BD: solo patrones activos, ordenados por prioridad
    patterns = IntentPattern.query.filter_by(
        is_active=True
    ).order_by(IntentPattern.priority).all()

    result = {}
    for p in patterns:
        category = p.intent_type  # CHAT_RAG, AGENT_TOOLS, etc.
        if category not in result:
            result[category] = []
        result[category].append(p.regex_pattern)

    r.setex(CACHE_KEY, CACHE_TTL, json.dumps(result))
    return result

# Extraído de: LibroCyberrange/cap-09-fastapi-escala.md
# backend/routers/gaming.py — Rate limiter en memoria para flags
from collections import defaultdict
import time as _time

# Cache en memoria: {user_id: [timestamps de intentos]}
_flag_attempts: dict[int, list[float]] = defaultdict(list)
FLAG_RATE_LIMIT = 10    # máximo 10 intentos
FLAG_RATE_WINDOW = 60   # por cada 60 segundos

def _check_rate_limit(user_id: int) -> bool:
    """Retorna True si el usuario excede el rate limit."""
    now = _time.time()
    attempts = _flag_attempts[user_id]
    # Limpiar intentos fuera de la ventana
    _flag_attempts[user_id] = [t for t in attempts if now - t < FLAG_RATE_WINDOW]
    if len(_flag_attempts[user_id]) >= FLAG_RATE_LIMIT:
        return True
    _flag_attempts[user_id].append(now)
    return False

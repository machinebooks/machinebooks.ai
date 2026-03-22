# Extraído de: LibroTecnico/cap-07-api-rest.md
# backend/middleware/rate_limit.py
from functools import wraps
from flask import g, jsonify, current_app
import redis
import time

def _get_redis_client():
    """Acceso lazy a Redis — debe llamarse dentro de un contexto de aplicación Flask."""
    return redis.Redis.from_url(current_app.config['REDIS_URL'])

def rate_limit(max_requests: int, window_seconds: int, key_prefix: str = "rl"):
    """Tercera capa: rate limiting con ventana deslizante en Redis.
    Diferencia por usuario y por tipo de operación."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user_id = getattr(g.current_user, 'id', 'anonymous')
            # La clave incluye el tipo de operación para diferenciación
            redis_key = f"{key_prefix}:{user_id}:{f.__name__}"
            now = time.time()
            window_start = now - window_seconds
            redis_client = _get_redis_client()

            pipe = redis_client.pipeline()
            # Limpiar entradas fuera de la ventana y contar las que quedan
            pipe.zremrangebyscore(redis_key, 0, window_start)
            pipe.zcard(redis_key)
            pipe.zadd(redis_key, {str(now): now})
            pipe.expire(redis_key, window_seconds)
            results = pipe.execute()

            request_count = results[1]
            if request_count >= max_requests:
                # Calcular cuánto debe esperar el cliente: el tiempo restante
                # hasta que la petición más antigua salga de la ventana
                oldest = redis_client.zrange(redis_key, 0, 0, withscores=True)
                if oldest:
                    retry_after = int(window_seconds - (now - oldest[0][1]))
                else:
                    retry_after = int(window_seconds)
                response = jsonify({'error': 'Demasiadas peticiones'})
                response.headers['Retry-After'] = max(retry_after, 1)
                return response, 429

            return f(*args, **kwargs)
        return decorated
    return decorator

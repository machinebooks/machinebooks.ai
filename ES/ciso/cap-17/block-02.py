# Extraído de: LibroCISO/cap-17-hardening-siem.md
# Ejemplo didáctico: middleware/rate_limit.py

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.extensions import redis_client


# Configuración de límites por categoría
RATE_LIMITS = {
    "auth": {"max_requests": 10, "window_seconds": 60},
    "ai": {"max_requests": 20, "window_seconds": 3600},
    "default": {"max_requests": 100, "window_seconds": 60},
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting diferenciado por categoría de endpoint.

    Usa Redis como backend de contadores con TTL automático.
    Fail-closed para endpoints sensibles (auth, AI) cuando Redis
    no está disponible. Solo fail-open para API general.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Solo aplicar a la API, no a archivos estáticos
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        category = self._classify_endpoint(request.url.path)
        limit_config = RATE_LIMITS[category]
        client_ip = request.client.host if request.client else "unknown"

        try:
            is_allowed, remaining, reset_at = await self._check_limit(
                client_ip, category, limit_config
            )
        except Exception:
            # Fail-closed para endpoints sensibles (auth, AI)
            if category in ("auth", "ai"):
                return JSONResponse(
                    status_code=503,
                    content={
                        "error": "service_temporarily_unavailable",
                        "detail": "Backend de rate limiting no disponible. Reinténtelo.",
                    },
                    headers={"Retry-After": "30"},
                )
            # Fail-open solo para endpoints generales de API
            return await call_next(request)

        if not is_allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "detail": (
                        f"Límite de {limit_config['max_requests']} "
                        f"peticiones por {limit_config['window_seconds']}s "
                        f"excedido para categoría '{category}'."
                    ),
                    "retry_after": reset_at,
                },
                headers={
                    "Retry-After": str(reset_at),
                    "X-RateLimit-Limit": str(limit_config["max_requests"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Category": category,
                },
            )

        response = await call_next(request)

        # Headers informativos de rate limiting
        response.headers["X-RateLimit-Limit"] = str(
            limit_config["max_requests"]
        )
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Category"] = category

        return response

    @staticmethod
    def _classify_endpoint(path: str) -> str:
        """Clasifica el endpoint en una categoría de rate limiting."""
        if "/auth/" in path or path.endswith("/login"):
            return "auth"
        elif "/ai/" in path or "/agents/" in path or "/chat/" in path:
            return "ai"
        return "default"

    @staticmethod
    async def _check_limit(
        client_ip: str, category: str, config: dict
    ) -> tuple[bool, int, int]:
        """Verifica el límite usando ventana deslizante en Redis.

        Retorna (permitido, peticiones_restantes, segundos_para_reset).
        """
        window = config["window_seconds"]
        max_req = config["max_requests"]
        now = int(time.time())
        window_key = now // window

        key = f"ratelimit:{client_ip}:{category}:{window_key}"

        # INCR atómico + TTL en una sola transacción
        pipe = redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        results = await pipe.execute()

        current_count = results[0]
        remaining = max(0, max_req - current_count)
        reset_at = (window_key + 1) * window - now

        return current_count <= max_req, remaining, reset_at

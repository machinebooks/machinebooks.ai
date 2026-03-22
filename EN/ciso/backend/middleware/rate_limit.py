# Chapter 17 — RateLimitMiddleware with Redis
#
# Differentiated rate limiting by endpoint category:
# - Authentication (/api/auth/*): 10 req/min (brute force prevention)
# - AI (/api/ai/*, /api/agents/*): 20 req/hour (token cost control)
# - General (everything else): 100 req/min (script protection)
#
# Fail-open design: if Redis is unavailable, requests pass through.
# Rate limiting is a protection layer, not a functional requirement.

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


# Limits per endpoint category
RATE_LIMITS = {
    "auth": {"max_requests": 10, "window_seconds": 60},
    "ai": {"max_requests": 20, "window_seconds": 3600},
    "default": {"max_requests": 100, "window_seconds": 60},
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting differentiated by endpoint category.

    Uses Redis as counter backend with automatic TTL.
    If Redis is unavailable, allows traffic through (fail-open).
    """

    def __init__(self, app, redis_client=None):
        super().__init__(app)
        self.redis = redis_client

    async def dispatch(self, request: Request, call_next) -> Response:
        # Only apply to API endpoints, not static files
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        category = self._classify_endpoint(request.url.path)
        limit_config = RATE_LIMITS[category]
        client_ip = request.client.host if request.client else "unknown"

        try:
            is_allowed, remaining, reset_at = await self._check_limit(
                client_ip, category, limit_config,
            )
        except Exception:
            # Fail-open: if Redis fails, do not block legitimate traffic
            return await call_next(request)

        if not is_allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "detail": (
                        f"Limit of {limit_config['max_requests']} requests "
                        f"per {limit_config['window_seconds']}s exceeded "
                        f"for category '{category}'."
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

        # Informational rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit_config["max_requests"])
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Category"] = category

        return response

    @staticmethod
    def _classify_endpoint(path: str) -> str:
        """Classify the endpoint into a rate limiting category."""
        if "/auth/" in path or path.endswith("/login"):
            return "auth"
        elif "/ai/" in path or "/agents/" in path or "/copilot/" in path:
            return "ai"
        return "default"

    async def _check_limit(
        self, client_ip: str, category: str, config: dict,
    ) -> tuple[bool, int, int]:
        """Check and increment the rate limit counter in Redis.

        Returns: (is_allowed, remaining_requests, seconds_until_reset)
        """
        if not self.redis:
            return True, config["max_requests"], 0

        window = config["window_seconds"]
        key = f"ratelimit:{client_ip}:{category}:{int(time.time()) // window}"

        # Atomic increment + TTL
        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, window)

        remaining = max(0, config["max_requests"] - current)
        ttl = await self.redis.ttl(key)
        is_allowed = current <= config["max_requests"]

        return is_allowed, remaining, max(0, ttl)

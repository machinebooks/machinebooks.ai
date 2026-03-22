# Extraído de: LibroCISO/cap-17-hardening-siem.md
# Ejemplo didáctico: middleware/security_headers.py

import secrets
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Inyecta headers de seguridad en toda respuesta HTTP.

    El nonce CSP se genera por petición y se almacena
    en request.state para que el template HTML lo use.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Generar nonce criptográfico único por petición
        nonce = secrets.token_urlsafe(32)
        request.state.csp_nonce = nonce

        response = await call_next(request)

        # Content-Security-Policy con nonce
        csp = (
            f"default-src 'self'; "
            f"script-src 'self' 'nonce-{nonce}'; "
            f"style-src 'self' 'unsafe-inline'; "  # Tailwind necesita inline styles
            f"img-src 'self' data: blob:; "
            f"font-src 'self'; "
            f"connect-src 'self'; "
            f"frame-ancestors 'none'; "
            f"base-uri 'self'; "
            f"form-action 'self'"
        )
        response.headers["Content-Security-Policy"] = csp

        # HSTS: un año, subdominios, preload
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

        # Prevenir clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Prevenir MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Controlar información en Referer
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Desactivar funciones innecesarias del navegador
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), "
            "payment=(), usb=(), magnetometer=()"
        )

        # No cachear respuestas con datos sensibles
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, max-age=0"
            )
            response.headers["Pragma"] = "no-cache"

        return response

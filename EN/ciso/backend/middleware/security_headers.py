# Chapter 17 — SecurityHeadersMiddleware
#
# First middleware in the stack. Ensures EVERY response includes
# browser security headers: CSP with per-request nonces, HSTS with
# preload, X-Frame-Options, X-Content-Type-Options, Referrer-Policy,
# and Permissions-Policy. API responses also get no-cache directives.

import secrets
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Injects security headers into every HTTP response.

    The CSP nonce is generated per request and stored in
    request.state for the HTML template to use with <script> tags.

    Design note: style-src uses 'unsafe-inline' because Tailwind CSS
    generates inline styles dynamically. This is a documented concession —
    the risk of CSS-based data exfiltration is lower than script injection,
    and other layers (audit, RBAC, encryption) mitigate the impact.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate a cryptographic nonce unique to this request
        nonce = secrets.token_urlsafe(32)
        request.state.csp_nonce = nonce

        response = await call_next(request)

        # Content-Security-Policy with nonce
        csp = (
            f"default-src 'self'; "
            f"script-src 'self' 'nonce-{nonce}'; "
            f"style-src 'self' 'unsafe-inline'; "
            f"img-src 'self' data: blob:; "
            f"font-src 'self'; "
            f"connect-src 'self'; "
            f"frame-ancestors 'none'; "
            f"base-uri 'self'; "
            f"form-action 'self'"
        )
        response.headers["Content-Security-Policy"] = csp

        # HSTS: one year, subdomains, preload
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Control Referer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Disable unnecessary browser features
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), "
            "payment=(), usb=(), magnetometer=()"
        )

        # No-cache for API responses (contain sensitive data)
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, max-age=0"
            )
            response.headers["Pragma"] = "no-cache"

        return response

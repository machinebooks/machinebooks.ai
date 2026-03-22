# Extraído de: LibroTecnico/cap-07-api-rest.md
# backend/middleware/security_headers.py

def init_security_headers(app):
    """Aplica cabeceras de seguridad OWASP a todas las respuestas.
    Centralizado para garantizar consistencia en los 190+ endpoints."""

    @app.after_request
    def add_security_headers(response):
        # CSP restrictiva: solo permite recursos del mismo origen
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'"
        )
        # HSTS: fuerza HTTPS durante 1 año, incluye subdominios
        response.headers['Strict-Transport-Security'] = (
            'max-age=31536000; includeSubDomains; preload'
        )
        # Prevención de clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        # Prevención de MIME sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # Deshabilitar APIs del navegador no utilizadas
        response.headers['Permissions-Policy'] = (
            'geolocation=(), camera=(), microphone=(), '
            'payment=(), usb=(), magnetometer=()'
        )
        # Eliminar cabecera que revela el servidor web
        response.headers.pop('Server', None)
        return response

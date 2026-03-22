# Extraído de: LibroTecnico/cap-06-iam-seguridad.md
@app.after_request
def apply_security_headers(response):
    """Cabeceras OWASP en toda respuesta — sin excepciones."""
    # Content Security Policy estricta — solo recursos del mismo origen
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; font-src 'self'; connect-src 'self'; "
        "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    )
    # HSTS con preload — fuerza HTTPS durante 1 año, incluye subdominios
    response.headers['Strict-Transport-Security'] = (
        'max-age=31536000; includeSubDomains; preload'
    )
    # Prevenir clickjacking — ningún frame externo puede embeber la app
    response.headers['X-Frame-Options'] = 'DENY'
    # Prevenir MIME sniffing — el navegador no infiere tipos de contenido
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Bloquear acceso a sensores del dispositivo
    response.headers['Permissions-Policy'] = (
        'geolocation=(), camera=(), microphone=()'
    )
    # Referrer restringido — no filtrar URLs en peticiones cross-origin
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    # Aislamiento cross-origin — prevenir ataques Spectre y side-channel
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Resource-Policy'] = 'same-origin'
    return response

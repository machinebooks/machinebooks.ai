# Extraído de: LibroCyberrange/cap-24-seguridad-plataforma.md
# Obtención de IP real del cliente detrás de proxies
# Fichero: cyber-range-builder/backend/services/audit_service.py

@staticmethod
def _get_client_ip(request: Request) -> str:
    """Obtener IP del cliente considerando proxies.
    Orden de prioridad: X-Forwarded-For > X-Real-IP > IP directa.
    NOTA: En producción, solo confiar en estos headers si el proxy
    es de confianza — un atacante puede falsificar X-Forwarded-For."""
    forwarded_for = request.headers.get('x-forwarded-for')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()

    real_ip = request.headers.get('x-real-ip')
    if real_ip:
        return real_ip

    if hasattr(request.client, 'host'):
        return request.client.host

    return 'unknown'

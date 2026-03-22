# Extraído de: LibroTecnico/cap-07-api-rest.md
# backend/middleware/request_context.py
import uuid
import time
from flask import g, request
import structlog

logger = structlog.get_logger()

def init_request_context(app):
    """Registra el middleware de contexto de petición en la aplicación Flask.
    Se ejecuta antes de cualquier función de vista."""

    @app.before_request
    def set_request_context():
        # El request_id permite correlacionar logs entre servicios
        g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        g.request_start_time = time.time()

    # Registrado fuera de before_request para evitar acumular handlers
    @app.after_request
    def add_correlation_id(response):
        response.headers['X-Request-ID'] = g.request_id
        # Calcular y registrar el tiempo total de respuesta
        duration_ms = (time.time() - g.request_start_time) * 1000
        logger.info(
            "request_completed",
            request_id=g.request_id,
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2)
        )
        return response

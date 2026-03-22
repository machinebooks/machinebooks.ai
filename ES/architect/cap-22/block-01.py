# Extraído de: LibroTecnico/cap-22-observabilidad.md
from flask import g, request
import time
import uuid

def register_request_logging_middleware(app):
    """Registra middlewares de timing y correlación de peticiones."""

    @app.before_request
    def start_timer():
        # Genera o propaga el request_id desde cabecera X-Request-ID
        # Esto permite rastrear peticiones que vienen de otros servicios
        g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        g.request_start_time = time.monotonic()

        # Añade el request_id a la respuesta para que el cliente pueda correlacionar
        g.logger = structlog.get_logger().bind(
            request_id=g.request_id,
            method=request.method,
            path=request.path,
            user_id=getattr(g, "current_user_id", None)
        )

    @app.after_request
    def log_request(response):
        duration_ms = (time.monotonic() - g.request_start_time) * 1000

        g.logger.info(
            "http_request",
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            content_length=response.content_length,
        )

        # Propaga el request_id en la respuesta HTTP
        response.headers["X-Request-ID"] = g.request_id
        return response

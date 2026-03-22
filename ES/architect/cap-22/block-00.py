# Extraído de: LibroTecnico/cap-22-observabilidad.md
import structlog
import uuid
from flask import g, request

def configure_logging(app):
    """Configura structlog con salida JSON en producción,
    texto formateado en desarrollo."""

    # Procesadores comunes a todos los entornos
    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        # Añade el request_id a cada log si estamos en contexto de petición
        _add_request_id,
    ]

    if app.config.get("ENV") == "production":
        # JSON estructurado en producción — parseable por sistemas de análisis
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer()
        ]
    else:
        # Texto coloreado en desarrollo — legible para humanos
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Suprimir logs verbosos de werkzeug y sqlalchemy en producción
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return structlog.get_logger()

def _add_request_id(logger, method, event_dict):
    """Processor de structlog: añade request_id al log si existe en contexto Flask."""
    try:
        event_dict["request_id"] = g.request_id
    except RuntimeError:
        pass  # Fuera de contexto de petición (tareas Celery, startup)
    return event_dict

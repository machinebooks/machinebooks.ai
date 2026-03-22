# Extraído de: LibroCISO/cap-22-observabilidad-siem.md
import structlog
import logging
import sys
from datetime import datetime, timezone


def add_grc_context(logger, method_name, event_dict):
    """Procesador que añade contexto GRC obligatorio a cada log."""
    # Timestamp ISO 8601 en UTC (requisito ENS op.exp.8)
    event_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
    # Identificador de instancia del servicio
    event_dict["service"] = event_dict.get("service", "grc-backend")
    # Nivel de severidad normalizado para SIEM
    event_dict["severity"] = method_name.upper()
    return event_dict


def configure_structlog():
    """Configura structlog con procesadores para compliance."""
    structlog.configure(
        processors=[
            # Añade contexto del thread local (request_id, user_id, etc.)
            structlog.contextvars.merge_contextvars,
            # Añade campos GRC obligatorios
            add_grc_context,
            # Filtra por nivel configurado
            structlog.stdlib.filter_by_level,
            # Añade nombre del logger
            structlog.stdlib.add_logger_name,
            # Formatea excepciones de forma legible
            structlog.processors.format_exc_info,
            # Renderiza a JSON para procesamiento automatizado
            structlog.processors.JSONRenderer(sort_keys=True),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Uso en el código de la aplicación
log = structlog.get_logger()

# En un middleware de autenticación:
log.info(
    "auth_success",
    user_id="usr_12345",
    corporate_id="corp_001",
    ip="10.0.1.42",
    method="JWT",
    mfa_used=True,
    module_accessed="risk_management",
    request_id="req_abc123",
)
# Produce JSON:
# {
#   "event": "auth_success",
#   "user_id": "usr_12345",
#   "corporate_id": "corp_001",
#   "ip": "10.0.1.42",
#   "method": "JWT",
#   "mfa_used": true,
#   "module_accessed": "risk_management",
#   "request_id": "req_abc123",
#   "timestamp": "2025-03-15T14:32:07.123456+00:00",
#   "service": "grc-backend",
#   "severity": "INFO"
# }

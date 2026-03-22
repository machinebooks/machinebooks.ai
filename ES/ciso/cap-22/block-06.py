# Extraído de: LibroCISO/cap-22-observabilidad-siem.md
import uuid
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

log = structlog.get_logger()


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Middleware que inyecta contexto de observabilidad en cada request."""

    async def dispatch(self, request: Request, call_next):
        # Generar request_id único para trazabilidad end-to-end
        request_id = request.headers.get(
            "X-Request-ID",
            str(uuid.uuid4())
        )

        # Extraer información del usuario autenticado
        user_id = getattr(request.state, "user_id", "anonymous")
        corporate_id = getattr(request.state, "corporate_id", "unknown")

        # Inyectar contexto que se propagará a TODOS los logs
        # generados durante esta solicitud
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            user_id=user_id,
            corporate_id=corporate_id,
            client_ip=request.client.host if request.client else "unknown",
            method=request.method,
            path=request.url.path,
            user_agent=request.headers.get("user-agent", "unknown"),
        )

        # Log de inicio de solicitud
        log.info("request_started")

        try:
            response = await call_next(request)

            # Log de fin de solicitud con código de estado
            log.info(
                "request_completed",
                status_code=response.status_code,
            )

            # Propagar request_id en la respuesta para trazabilidad
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as exc:
            log.error(
                "request_failed",
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            raise

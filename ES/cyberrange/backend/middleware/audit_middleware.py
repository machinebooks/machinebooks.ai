# Extraído de: LibroCyberrange/cap-09-fastapi-escala.md
# backend/middleware/audit_middleware.py — Versión didáctica
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time, uuid
from typing import Callable

class AuditMiddleware(BaseHTTPMiddleware):
    """Intercepta todas las peticiones HTTP para auditoría automática."""

    # Rutas de alta prioridad: siempre se auditan
    HIGH_PRIORITY_PATHS = {
        '/api/auth/login', '/api/auth/logout',
        '/api/admin/', '/api/admin/users/',
        '/api/admin/workzones/', '/api/admin/machines/',
        '/api/admin/playbooks/', '/api/scenarios/',
        '/api/challenges/'
    }

    # Rutas excluidas: documentación, health checks
    EXCLUDED_PATHS = {
        '/api/health', '/api/docs', '/api/openapi.json',
        '/api/redoc', '/metrics', '/favicon.ico'
    }

    # Solo métodos que modifican datos generan evento por defecto
    AUDIT_METHODS = {'POST', 'PUT', 'DELETE', 'PATCH'}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Identificador único para correlación
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.time()
        method = request.method
        path = request.url.path

        should_audit = self._should_audit_request(method, path)

        try:
            response = await call_next(request)
        except Exception as e:
            if should_audit:
                await self._log_error_event(request_id, method, path, e)
            raise
        finally:
            duration_ms = int((time.time() - start_time) * 1000)
            if should_audit:
                event_type, category, action = self._categorize_request(method, path)
                severity = self._determine_severity(method, path,
                    response.status_code if response else 500)
                await self._log_request_event(
                    request_id, method, path, duration_ms,
                    event_type, category, action, severity
                )

        return response

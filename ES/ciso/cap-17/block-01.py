# Extraído de: LibroCISO/cap-17-hardening-siem.md
# Ejemplo didáctico: middleware/audit.py

import json
import logging
import socket
import time
from datetime import datetime, timezone
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Logger configurado para enviar al SIEM vía Syslog
siem_logger = logging.getLogger("siem")

MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class AuditMiddleware(BaseHTTPMiddleware):
    """Registra operaciones mutantes en BD y SIEM simultáneamente.

    Solo intercepta POST, PUT, PATCH, DELETE.
    Los GET no se auditan para evitar volumen excesivo.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method not in MUTATING_METHODS:
            return await call_next(request)

        start_time = time.time()

        # Extraer información del usuario del token JWT (si existe)
        user_id = getattr(request.state, "user_id", "anonymous")
        corporate_id = getattr(request.state, "corporate_id", "unknown")
        client_ip = request.client.host if request.client else "unknown"
        request_id = getattr(request.state, "request_id", "no-id")

        response = await call_next(request)

        duration_ms = int((time.time() - start_time) * 1000)

        # 1. Registro en base de datos (consulta interna del DPO)
        audit_entry = {
            "user_id": user_id,
            "corporate_id": corporate_id,
            "action": request.method,
            "resource": str(request.url.path),
            "status_code": response.status_code,
            "ip_address": client_ip,
            "user_agent": request.headers.get("user-agent", ""),
            "request_id": request_id,
            "duration_ms": duration_ms,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        # Inserción asíncrona en tabla audit_trail
        await self._persist_to_database(audit_entry)

        # 2. Forwarding al SIEM en formato CEF
        cef_message = self._format_cef(audit_entry)
        siem_logger.info(cef_message)

        return response

    async def _persist_to_database(self, entry: dict) -> None:
        """Inserta el registro de auditoría en la tabla audit_trail.

        Usa una sesión de BD independiente para no interferir
        con la transacción de la petición principal.
        """
        from app.database import async_session_audit
        from app.models.audit import AuditTrail

        async with async_session_audit() as session:
            record = AuditTrail(**entry)
            session.add(record)
            await session.commit()

    @staticmethod
    def _escape_cef_field(value: str) -> str:
        """Escapa caracteres especiales en valores de extensión CEF.

        CEF requiere escapar: backslash, pipe, igual y saltos de línea.
        Sin escapado, un atacante puede inyectar campos CEF falsos
        o corromper el parsing de eventos en el SIEM.
        """
        if not isinstance(value, str):
            value = str(value)
        return (
            value
            .replace("\\", "\\\\")
            .replace("|", "\\|")
            .replace("=", "\\=")
            .replace("\n", "\\n")
            .replace("\r", "\\r")
        )

    def _format_cef(self, entry: dict) -> str:
        """Genera mensaje en formato CEF (Common Event Format).

        CEF es el formato estándar que los SIEM (QRadar, Splunk,
        ArcSight, Sentinel) consumen nativamente.

        Formato: CEF:Version|Vendor|Product|Version|EventID|Name|Severity|Extensions

        Todos los valores de extensión se escapan para prevenir inyección CEF.
        """
        # Mapear código de estado a severidad CEF (0-10)
        severity = self._status_to_severity(entry["status_code"])
        esc = self._escape_cef_field

        # Mapear método HTTP a ID de evento
        event_ids = {
            "POST": "100", "PUT": "200",
            "PATCH": "300", "DELETE": "400"
        }
        event_id = event_ids.get(entry["action"], "999")

        extensions = (
            f"src={esc(entry['ip_address'])} "
            f"suser={esc(entry['user_id'])} "
            f"cs1={esc(entry['corporate_id'])} cs1Label=TenantID "
            f"cs2={esc(entry['request_id'])} cs2Label=RequestID "
            f"request={esc(entry['resource'])} "
            f"outcome={entry['status_code']} "
            f"cn1={entry['duration_ms']} cn1Label=DurationMs "
            f"rt={esc(entry['timestamp'])}"
        )

        # El nombre del evento en la cabecera también se escapa
        event_name = esc(f"{entry['action']} {entry['resource']}")

        return (
            f"CEF:0|GRCPlatform|GRC|1.0|{event_id}|"
            f"{event_name}|"
            f"{severity}|{extensions}"
        )

    @staticmethod
    def _status_to_severity(status_code: int) -> int:
        """Mapea código HTTP a severidad CEF.

        Los 4xx se mapean a severidad media (posible ataque o error),
        los 5xx a severidad alta (fallo del sistema).
        """
        if 200 <= status_code < 300:
            return 1   # Informativo
        elif 300 <= status_code < 400:
            return 2   # Bajo
        elif status_code in (401, 403):
            return 6   # Alto — posible intento de acceso no autorizado
        elif 400 <= status_code < 500:
            return 4   # Medio
        elif status_code >= 500:
            return 8   # Muy alto — fallo del sistema
        return 3       # Desconocido → medio-bajo

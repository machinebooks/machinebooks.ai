# Chapter 17 — AuditMiddleware with dual logging (DB + SIEM/CEF)
#
# Captures every mutating operation (POST, PUT, PATCH, DELETE) and
# records it in two places simultaneously:
# 1. Database table `audit_trail` — for internal DPO queries
# 2. SIEM via Syslog in CEF format — for SOC correlation
#
# GET requests are NOT audited to avoid excessive volume.
# 401/403 responses are escalated to CEF severity 6 (high) because
# in a GRC platform they may indicate unauthorized access attempts.

import time
import logging
from datetime import datetime, timezone
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Logger configured to send to SIEM via Syslog
siem_logger = logging.getLogger("siem")

MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class AuditMiddleware(BaseHTTPMiddleware):
    """Records mutating operations in DB and SIEM simultaneously.

    Only intercepts POST, PUT, PATCH, DELETE.
    GET requests are not audited to avoid excessive volume.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method not in MUTATING_METHODS:
            return await call_next(request)

        start_time = time.time()

        # Extract user information from JWT token (if present)
        user_id = getattr(request.state, "user_id", "anonymous")
        corporate_id = getattr(request.state, "corporate_id", "unknown")
        client_ip = request.client.host if request.client else "unknown"
        request_id = getattr(request.state, "request_id", "no-id")

        response = await call_next(request)

        duration_ms = int((time.time() - start_time) * 1000)

        # 1. Record in database (for internal DPO queries)
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
        await self._persist_to_database(audit_entry)

        # 2. Forward to SIEM in CEF format
        cef_message = self._format_cef(audit_entry)
        siem_logger.info(cef_message)

        return response

    async def _persist_to_database(self, entry: dict) -> None:
        """Insert audit record into the audit_trail table.

        Uses an independent DB session to avoid interfering
        with the main request transaction.
        """
        # In production:
        # async with async_session_audit() as session:
        #     record = AuditTrail(**entry)
        #     session.add(record)
        #     await session.commit()
        pass

    def _format_cef(self, entry: dict) -> str:
        """Generate a CEF (Common Event Format) message.

        CEF is the standard format consumed natively by SIEM systems
        (QRadar, Splunk, ArcSight, Sentinel).

        Format: CEF:Version|Vendor|Product|Version|EventID|Name|Severity|Extensions
        """
        severity = self._status_to_severity(entry["status_code"])

        event_ids = {
            "POST": "100", "PUT": "200",
            "PATCH": "300", "DELETE": "400",
        }
        event_id = event_ids.get(entry["action"], "999")

        extensions = (
            f"src={entry['ip_address']} "
            f"suser={entry['user_id']} "
            f"cs1={entry['corporate_id']} cs1Label=TenantID "
            f"cs2={entry['request_id']} cs2Label=RequestID "
            f"request={entry['resource']} "
            f"outcome={entry['status_code']} "
            f"cn1={entry['duration_ms']} cn1Label=DurationMs "
            f"rt={entry['timestamp']}"
        )

        return (
            f"CEF:0|GRCPlatform|GRC|1.0|{event_id}|"
            f"{entry['action']} {entry['resource']}|"
            f"{severity}|{extensions}"
        )

    @staticmethod
    def _status_to_severity(status_code: int) -> int:
        """Map HTTP status to CEF severity.

        401/403 -> severity 6 (high): potential unauthorized access
        5xx -> severity 8 (very high): system failure
        """
        if 200 <= status_code < 300:
            return 1   # Informational
        elif 300 <= status_code < 400:
            return 2   # Low
        elif status_code in (401, 403):
            return 6   # High — possible unauthorized access attempt
        elif 400 <= status_code < 500:
            return 4   # Medium
        elif status_code >= 500:
            return 8   # Very high — system failure
        return 3       # Unknown -> medium-low

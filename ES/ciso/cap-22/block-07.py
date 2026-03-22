# Extraído de: LibroCISO/cap-22-observabilidad-siem.md
import socket
import structlog
from datetime import datetime, timezone

# Conexión Syslog persistente
SYSLOG_HOST = "siem.entidad.local"  # SIEM de la entidad
SYSLOG_PORT = 514
SYSLOG_FACILITY = 16  # local0

log = structlog.get_logger()


class CEFFormatter:
    """Formatea eventos de seguridad en CEF para envío al SIEM."""

    # Cabecera CEF: versión|vendor|producto|versión|id_evento|nombre|severidad
    CEF_HEADER = "CEF:0|GRC_Platform|SecurityAudit|1.0"

    # Mapeo de eventos a IDs y severidades CEF (0-10)
    EVENT_MAP = {
        "auth_success":       ("100", "Authentication Success", 3),
        "auth_failure":       ("101", "Authentication Failure", 5),
        "auth_mfa_required":  ("102", "MFA Challenge Issued", 3),
        "auth_mfa_failure":   ("103", "MFA Verification Failed", 7),
        "permission_denied":  ("200", "Access Denied", 6),
        "role_changed":       ("201", "User Role Modified", 7),
        "data_exported":      ("300", "Regulatory Data Exported", 5),
        "pii_detected":       ("301", "PII Detected in Content", 8),
        "ai_request":         ("400", "AI System Invocation", 3),
        "ai_guardrail_block": ("401", "AI Guardrail Triggered", 7),
        "ai_human_override":  ("402", "AI Output Rejected by User", 5),
        "config_changed":     ("500", "System Configuration Changed", 6),
        "backup_completed":   ("600", "Backup Completed", 2),
        "backup_failed":      ("601", "Backup Failed", 9),
    }

    def format_cef(self, event: str, fields: dict) -> str:
        """Genera un mensaje CEF a partir de un evento estructurado."""
        event_id, event_name, severity = self.EVENT_MAP.get(
            event, ("999", "Unknown Event", 5)
        )

        # Cabecera CEF
        header = f"{self.CEF_HEADER}|{event_id}|{event_name}|{severity}"

        # Extensiones CEF estándar
        extensions = []
        if "user_id" in fields:
            extensions.append(f"suser={fields['user_id']}")
        if "client_ip" in fields:
            extensions.append(f"src={fields['client_ip']}")
        if "request_id" in fields:
            extensions.append(f"cs1={fields['request_id']}")
            extensions.append("cs1Label=RequestID")
        if "corporate_id" in fields:
            extensions.append(f"cs2={fields['corporate_id']}")
            extensions.append("cs2Label=TenantID")
        if "path" in fields:
            extensions.append(f"requestURL={fields['path']}")
        if "method" in fields:
            extensions.append(f"requestMethod={fields['method']}")

        # Timestamp en formato CEF (epoch millis)
        now = datetime.now(timezone.utc)
        extensions.append(f"rt={int(now.timestamp() * 1000)}")

        return f"{header}|{' '.join(extensions)}"

    def send_to_siem(self, event: str, fields: dict):
        """Envía evento CEF al SIEM vía Syslog UDP."""
        cef_message = self.format_cef(event, fields)

        try:
            # Syslog UDP (RFC 5424)
            # NOTA: En producción, usar Syslog sobre TLS (RFC 5425)
            # o un agente local (Fluentd/Filebeat) que envíe cifrado.
            # UDP plano solo es aceptable en redes aisladas de confianza.
            priority = (SYSLOG_FACILITY * 8) + 6  # facility + severity
            syslog_msg = f"<{priority}>{cef_message}"

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(
                syslog_msg.encode("utf-8"),
                (SYSLOG_HOST, SYSLOG_PORT)
            )
            sock.close()
        except Exception as exc:
            # Si falla el envío al SIEM, loguear localmente
            # NUNCA silenciar un fallo de auditoría
            log.error(
                "siem_send_failed",
                event=event,
                error=str(exc),
            )


# Ejemplo de uso en un handler de autenticación:
cef = CEFFormatter()

# Cuando un login falla:
cef.send_to_siem("auth_failure", {
    "user_id": "usr_12345",
    "client_ip": "10.0.1.42",
    "request_id": "req_abc123",
    "corporate_id": "corp_001",
    "path": "/api/v1/auth/login",
    "method": "POST",
})
# Envía al SIEM:
# CEF:0|GRC_Platform|SecurityAudit|1.0|101|Authentication Failure|5|
#   suser=usr_12345 src=10.0.1.42 cs1=req_abc123 cs1Label=RequestID
#   cs2=corp_001 cs2Label=TenantID requestURL=/api/v1/auth/login
#   requestMethod=POST rt=1710512345678

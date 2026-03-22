# Extraído de: LibroCyberrange/cap-03-arquitecto-cyber-range.md
# Sistema de auditoría completo
# Ejemplo didáctico: patrones/audit/service.py

from enum import Enum
from datetime import datetime, timezone

class AuditSeverity(str, Enum):
    TRACE = "trace"        # Acciones rutinarias (login, navegación)
    INFO = "info"          # Acciones normales (submit flag, ver scoreboard)
    WARNING = "warning"    # Acciones sospechosas (acceso denegado, rate limit)
    ERROR = "error"        # Fallos de sistema (VM no arranca, playbook falla)
    CRITICAL = "critical"  # Eventos de seguridad (intento de escape, brute force)
    AUDIT = "audit"        # Acciones de compliance (cambio de permisos, export datos)

def audit_log(
    action: str,
    user_id: int = None,
    detail: str = None,
    severity: str = AuditSeverity.INFO,
    ip_address: str = None,
    workzone_id: int = None,
    exercise_id: int = None,
    metadata: dict = None
):
    """Registra una acción en el log de auditoría.

    Cada acción se persiste en MySQL y, si la severidad es WARNING
    o superior, se notifica al organizador en tiempo real por WebSocket.
    """
    entry = AuditLog(
        action=action,
        user_id=user_id,
        detail=detail,
        severity=severity,
        ip_address=ip_address,
        workzone_id=workzone_id,
        exercise_id=exercise_id,
        metadata_json=json.dumps(metadata) if metadata else None,
        created_at=datetime.now(timezone.utc)
    )
    db.session.add(entry)
    db.session.commit()

    # Notificación en tiempo real para eventos importantes
    if severity in (AuditSeverity.WARNING, AuditSeverity.CRITICAL):
        websocket_manager.emit_to_organizers(
            exercise_id=exercise_id,
            event="security_alert",
            data={
                "action": action,
                "severity": severity,
                "user_id": user_id,
                "detail": detail,
                "timestamp": entry.created_at.isoformat()
            }
        )

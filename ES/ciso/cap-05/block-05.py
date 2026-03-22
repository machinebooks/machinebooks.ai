# Extraído de: LibroCISO/cap-05-dpia-derechos.md
# Tarea Celery Beat: verificación diaria de plazos de derechos ARCO+
# Se ejecuta todos los días a las 08:00 — antes del inicio de jornada

from datetime import datetime, timedelta
from celery import shared_task
from app.models.privacy import SubjectRightsRequest, RequestStatus

# Estados que indican solicitudes abiertas (no cerradas ni notificadas)
OPEN_STATUSES = [
    RequestStatus.RECEIVED,
    RequestStatus.IDENTITY_VERIFICATION,
    RequestStatus.IN_PROGRESS,
    RequestStatus.EXTENDED,
]


@shared_task(name="privacy.check_rights_deadlines")
def check_rights_deadlines():
    """Verifica plazos de todas las solicitudes de derechos abiertas.

    Genera alertas en tres niveles:
    - WARNING: 15 días desde recepción (queda la mitad del plazo)
    - URGENT: 23 días (quedan 7 días)
    - CRITICAL: 29 días (vence mañana)
    - OVERDUE: plazo excedido

    Las alertas se envían al DPO y al responsable asignado.
    Se registran en el sistema de notificaciones y en el audit trail.
    """
    now = datetime.utcnow()

    # Obtener todas las solicitudes abiertas de todos los tenants
    open_requests = (
        SubjectRightsRequest.query
        .filter(SubjectRightsRequest.status.in_(OPEN_STATUSES))
        .filter(SubjectRightsRequest.deleted_at.is_(None))
        .all()
    )

    alerts = []

    for request in open_requests:
        days_elapsed = (now - request.received_date).days
        days_remaining = (request.deadline_date - now).days

        alert_level = None

        if days_remaining < 0:
            alert_level = "OVERDUE"
        elif days_remaining <= 1:
            alert_level = "CRITICAL"
        elif days_remaining <= 7:
            alert_level = "URGENT"
        elif days_elapsed >= 15 and request.status == RequestStatus.RECEIVED:
            # 15 días y todavía en estado "recibida" — no se ha empezado
            alert_level = "WARNING"

        if alert_level:
            alerts.append({
                "request_id": request.id,
                "code": request.code,
                "right_type": request.right_type.value,
                "corporate_id": request.corporate_id,
                "alert_level": alert_level,
                "days_remaining": max(days_remaining, 0),
                "days_elapsed": days_elapsed,
                "status": request.status.value,
                "assigned_to": request.assigned_to,
                "deadline": request.deadline_date.isoformat(),
            })

            # Notificar al DPO y al responsable asignado
            notify_deadline_alert(
                corporate_id=request.corporate_id,
                alert_level=alert_level,
                request_code=request.code,
                right_type=request.right_type.value,
                days_remaining=max(days_remaining, 0),
                assigned_to=request.assigned_to,
            )

    # Registrar ejecución en audit trail
    audit_log_sync(
        action="privacy.deadline_check_completed",
        details={
            "total_open": len(open_requests),
            "alerts_generated": len(alerts),
            "overdue": len([a for a in alerts if a["alert_level"] == "OVERDUE"]),
            "critical": len([a for a in alerts if a["alert_level"] == "CRITICAL"]),
            "urgent": len([a for a in alerts if a["alert_level"] == "URGENT"]),
            "warning": len([a for a in alerts if a["alert_level"] == "WARNING"]),
        }
    )

    return {
        "checked": len(open_requests),
        "alerts": len(alerts),
        "details": alerts,
    }

# Extraído de: LibroCISO/cap-21-celery-async.md
@shared_task(
    name="app.tasks.notifications.check_breach_deadlines",
    queue="notifications",
    soft_time_limit=60,
    time_limit=90,
)
def check_breach_deadlines():
    """
    Verifica brechas de seguridad con plazos RGPD próximos a vencer.
    - Art. 33: notificación a la autoridad en 72 horas
    - Art. 34: comunicación al interesado sin dilación indebida
    """
    from app.models import SecurityBreach, BreachStatus
    from app.services.notification_service import NotificationService
    from app.database import get_session
    from datetime import datetime, timedelta

    session = get_session()
    notifier = NotificationService(session)
    now = datetime.utcnow()

    # Brechas detectadas pero NO notificadas a la autoridad
    open_breaches = session.query(SecurityBreach).filter(
        SecurityBreach.status.in_([
            BreachStatus.DETECTED,
            BreachStatus.INVESTIGATING,
            BreachStatus.CONFIRMED,
        ]),
        SecurityBreach.notified_to_authority.is_(False),
    ).all()

    for breach in open_breaches:
        hours_elapsed = (now - breach.detected_at).total_seconds() / 3600
        hours_remaining = 72 - hours_elapsed

        if hours_remaining <= 0:
            # VENCIDO: plazo de 72h superado
            notifier.send_critical_alert(
                tenant_id=breach.tenant_id,
                title="URGENTE: Plazo de 72h SUPERADO para brecha",
                body=(
                    f"La brecha '{breach.reference}' detectada el "
                    f"{breach.detected_at:%d/%m/%Y %H:%M} ha superado "
                    f"el plazo de 72 horas del Art. 33 RGPD sin "
                    f"notificación a la AEPD."
                ),
                escalate_to_ciso=True,
                send_email=True,
            )
        elif hours_remaining <= 12:
            # URGENTE: menos de 12 horas restantes
            notifier.send_urgent_alert(
                tenant_id=breach.tenant_id,
                title=f"Brecha '{breach.reference}': {hours_remaining:.0f}h restantes",
                body=(
                    f"Quedan {hours_remaining:.0f} horas para el plazo "
                    f"de notificación del Art. 33 RGPD."
                ),
                escalate_to_ciso=True,
                send_email=True,
            )
        elif hours_remaining <= 24:
            # ATENCIÓN: menos de 24 horas restantes
            notifier.send_warning_alert(
                tenant_id=breach.tenant_id,
                title=f"Brecha '{breach.reference}': {hours_remaining:.0f}h restantes",
                body=(
                    f"Quedan {hours_remaining:.0f} horas para el plazo "
                    f"de notificación a la autoridad de control."
                ),
                send_email=False,  # Solo notificación interna
            )

    session.close()
    return {"breaches_checked": len(open_breaches)}


@shared_task(
    name="app.tasks.notifications.check_rights_deadlines",
    queue="notifications",
    soft_time_limit=60,
    time_limit=90,
)
def check_rights_deadlines():
    """
    Verifica solicitudes de derechos del interesado (Art. 15-22 RGPD).
    Plazo legal: 1 mes desde la recepción (Art. 12.3).
    Alerta temprana: a los 25 días.
    """
    from app.models import SubjectRightsRequest, RequestStatus
    from app.services.notification_service import NotificationService
    from app.database import get_session
    from datetime import datetime, timedelta

    session = get_session()
    notifier = NotificationService(session)
    now = datetime.utcnow()

    pending_requests = session.query(SubjectRightsRequest).filter(
        SubjectRightsRequest.status.in_([
            RequestStatus.RECEIVED,
            RequestStatus.IN_PROGRESS,
            RequestStatus.PENDING_VALIDATION,
        ]),
    ).all()

    alerts_sent = 0
    for request in pending_requests:
        days_elapsed = (now - request.received_at).days
        days_remaining = 30 - days_elapsed

        if days_remaining <= 0:
            notifier.send_critical_alert(
                tenant_id=request.tenant_id,
                title="URGENTE: Plazo de 30 días SUPERADO para derecho ARCO+",
                body=(
                    f"La solicitud de {request.right_type} "
                    f"(ref: {request.reference}) ha superado el plazo "
                    f"de respuesta del Art. 12.3 RGPD."
                ),
                escalate_to_ciso=True,
                send_email=True,
            )
            alerts_sent += 1
        elif days_remaining <= 5:
            notifier.send_urgent_alert(
                tenant_id=request.tenant_id,
                title=f"Derecho ARCO+: {days_remaining} días restantes",
                body=(
                    f"La solicitud '{request.reference}' vence en "
                    f"{days_remaining} días."
                ),
                escalate_to_ciso=True,
                send_email=True,
            )
            alerts_sent += 1

    session.close()
    return {"requests_checked": len(pending_requests), "alerts_sent": alerts_sent}

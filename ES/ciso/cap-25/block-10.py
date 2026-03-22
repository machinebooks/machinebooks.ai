# Extraído de: LibroCISO/cap-25-vigilancia-normativa.md
@shared_task(name="regulatory_watch.escalate_unacknowledged")
def escalate_unacknowledged_critical_alerts():
    """Escala alertas críticas sin confirmar tras 48 horas.

    Ejecutada por Celery Beat cada 6 horas.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
    unacknowledged = get_critical_alerts_before(cutoff)

    for alert in unacknowledged:
        send_escalation_email(
            to=get_ciso_email(alert.corporate_id),
            subject=f"[ESCALACIÓN] Alerta normativa crítica #{alert.id}",
            body=f"La alerta '{alert.message}' lleva más de 48h "
                 f"sin confirmar. Requiere atención inmediata."
        )
        log_escalation(alert.id, "email_ciso")

# Extraído de: LibroCISO/cap-26-politicas-concienciacion.md
from celery import shared_task
from datetime import datetime, timezone

@shared_task(name="policy_awareness.check_review_dates")
def check_policy_review_dates():
    """Verifica políticas cuya fecha de revisión ha vencido.

    Si review_due_at < ahora y status == 'published',
    marca la política como 'needs_update' y notifica al propietario.

    Ejecutada por Celery Beat semanalmente (domingos a las 08:00).
    """
    now = datetime.now(timezone.utc)
    overdue_policies = get_published_policies_past_review_date(now)

    for policy in overdue_policies:
        # Cambiar estado
        update_policy_status(policy.id, "needs_update")

        # Notificar al propietario
        if policy.owner:
            send_notification(
                to=policy.owner,
                subject=f"Revisión pendiente: {policy.title}",
                body=(
                    f"La política '{policy.title}' (v{policy.policy_version}) "
                    f"tenía revisión programada para "
                    f"{policy.review_due_at.strftime('%d/%m/%Y')}. "
                    f"Por favor, revísela y publique una nueva versión."
                )
            )

    return {"overdue_policies": len(overdue_policies)}

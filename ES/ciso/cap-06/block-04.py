# Extraído de: LibroCISO/cap-06-brechas-encargados-transferencias.md
# Tarea Celery: vigilancia del plazo de 72h para brechas
# Se ejecuta cada hora y genera alertas escaladas

from celery import shared_task
from datetime import datetime, timedelta
from app.models.privacy import DataBreach, BreachStatus
from app.services.notifications import send_notification
from app.core.database import get_db_session


@shared_task(name="privacy.check_breach_deadlines",
             queue="notifications")
def check_breach_deadlines():
    """Verifica brechas activas y genera alertas según urgencia.

    Se ejecuta cada hora (configurado en Beat scheduler).
    Niveles de alerta:
    - Amarillo: menos de 48h restantes
    - Rojo: menos de 24h restantes
    - Negro: plazo vencido (deadline superado)
    """
    with get_db_session() as db:
        # Brechas abiertas que no han sido notificadas a la AEPD
        open_breaches = db.query(DataBreach).filter(
            DataBreach.status.notin_([
                BreachStatus.NOTIFIED_AUTHORITY,
                BreachStatus.NOTIFIED_SUBJECTS,
                BreachStatus.CLOSED
            ]),
            DataBreach.deleted_at.is_(None)
        ).all()

        now = datetime.utcnow()
        alerts_generated = 0

        for breach in open_breaches:
            remaining = breach.notification_deadline - now
            hours_left = remaining.total_seconds() / 3600

            if hours_left <= 0:
                # PLAZO VENCIDO — alerta crítica
                send_notification(
                    recipients=["dpo", "ciso", "legal"],
                    level="critical",
                    title=f"BRECHA {breach.code}: PLAZO 72h VENCIDO",
                    message=(
                        f"La brecha '{breach.title}' ha superado "
                        f"el plazo de 72 horas (Art. 33 RGPD). "
                        f"Deadline: {breach.notification_deadline}. "
                        f"Estado actual: {breach.status.value}. "
                        f"ACCIÓN INMEDIATA REQUERIDA."
                    ),
                    breach_id=breach.id
                )
                alerts_generated += 1

            elif hours_left <= 24:
                # ALERTA ROJA — menos de 24 horas
                send_notification(
                    recipients=["dpo", "ciso"],
                    level="high",
                    title=f"BRECHA {breach.code}: Menos de 24h para deadline",
                    message=(
                        f"Quedan {hours_left:.1f} horas para el "
                        f"deadline de notificación a la AEPD. "
                        f"Brecha: '{breach.title}'. "
                        f"Severidad: {breach.severity.value}."
                    ),
                    breach_id=breach.id
                )
                alerts_generated += 1

            elif hours_left <= 48:
                # ALERTA AMARILLA — menos de 48 horas
                send_notification(
                    recipients=["dpo"],
                    level="medium",
                    title=f"BRECHA {breach.code}: Menos de 48h para deadline",
                    message=(
                        f"Quedan {hours_left:.1f} horas. "
                        f"Brecha: '{breach.title}'."
                    ),
                    breach_id=breach.id
                )
                alerts_generated += 1

        return {
            "breaches_checked": len(open_breaches),
            "alerts_generated": alerts_generated,
            "checked_at": now.isoformat()
        }

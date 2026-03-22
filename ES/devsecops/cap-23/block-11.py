# Extraído de: LibroDevSecOps/cap-23-excepciones-deuda.md
from dataclasses import dataclass
from enum import Enum


class NotificationChannel(str, Enum):
    SLACK = "slack"
    EMAIL = "email"
    PIPELINE_COMMENT = "pipeline_comment"


@dataclass
class ExceptionNotification:
    """Notificación generada por el sistema de excepciones."""
    exception_id: int
    channel: NotificationChannel
    recipient: str
    subject: str
    body: str
    urgency: str  # info, warning, critical


def generate_notifications(actions: list[dict]) -> list[ExceptionNotification]:
    """Convierte acciones de revisión en notificaciones concretas."""
    notifications = []

    for action in actions:
        if action["action"] == "expired":
            # Notificación urgente al propietario y al security lead
            notifications.append(ExceptionNotification(
                exception_id=action["exception_id"],
                channel=NotificationChannel.SLACK,
                recipient=action["owner"],
                subject=f"Excepción #{action['exception_id']} expirada",
                body=(
                    f"La excepción para {action['finding_id']} ha expirado. "
                    f"El hallazgo volverá a bloquear el pipeline en el "
                    f"próximo PR que toque el componente afectado."
                ),
                urgency="critical"
            ))

        elif action["action"] == "expiring_soon":
            urgency = "warning" if action["days_remaining"] > 7 else "critical"
            notifications.append(ExceptionNotification(
                exception_id=action["exception_id"],
                channel=NotificationChannel.SLACK,
                recipient=action["owner"],
                subject=(
                    f"Excepción #{action['exception_id']} expira "
                    f"en {action['days_remaining']} días"
                ),
                body=action["message"],
                urgency=urgency
            ))

    return notifications

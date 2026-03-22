# Extraído de: LibroTecnico/cap-15-interfaces-chat.md
from celery import shared_task
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import get_db
from models.notification import Notification, NotificationType, NotificationPriority
from models.proposal import Proposal, ProposalStatus

@shared_task(queue='default', name='tasks.check_stalled_deals')
def check_stalled_deals():
    """
    Detecta propuestas activas sin actualización en >30 días
    y genera notificación DEAL_STALLED para el usuario responsable.
    Ejecuta en la cola 'default', programada cada hora por Celery Beat.
    """
    stall_threshold = datetime.utcnow() - timedelta(days=30)

    with get_db() as db:
        stalled_proposals = db.query(Proposal).filter(
            Proposal.status.in_([ProposalStatus.IN_REVIEW, ProposalStatus.SUBMITTED]),
            Proposal.updated_at < stall_threshold,
            Proposal.stall_notified == False  # Evitar notificaciones duplicadas
        ).all()

        for proposal in stalled_proposals:
            days_stalled = (datetime.utcnow() - proposal.updated_at).days

            notification = Notification(
                user_id=proposal.owner_id,
                type=NotificationType.DEAL_STALLED,
                priority=NotificationPriority.HIGH if days_stalled > 45 else NotificationPriority.MEDIUM,
                title=f"Propuesta sin movimiento: {proposal.title}",
                body=f"La propuesta '{proposal.title}' lleva {days_stalled} días sin actualizaciones. Revisa el estado.",
                action_url=f"/proposals/{proposal.id}",
                extra_data={
                    "proposal_id": proposal.id,
                    "days_stalled": days_stalled,
                    "last_updated": proposal.updated_at.isoformat(),
                    "proposal_value_eur": float(proposal.value_eur or 0)
                }
            )
            db.add(notification)
            proposal.stall_notified = True

        db.commit()

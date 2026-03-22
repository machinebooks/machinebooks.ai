# Extraído de: LibroFinOps/cap-21-aiact-auditoria.md
# tasks/retention.py
from celery import shared_task
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal
from models.llm_audit import LLMInteractionContent, LLMUsageLog
import logging

logger = logging.getLogger(__name__)


@shared_task(name="enforce_content_retention_policy")
def enforce_content_retention_policy():
    """
    Tarea diaria: elimina contenido de interacciones LLM expiradas.
    - Interacciones sin relevancia decisional: 90 días
    - Interacciones decision_relevant: se preservan en LLMAuditRecord
    Cumple RGPD Art. 5(1)(e): limitación del plazo de conservación.
    """
    db: Session = SessionLocal()
    try:
        expired = (
            db.query(LLMInteractionContent)
            .join(LLMUsageLog)
            .filter(
                LLMInteractionContent.expires_at <= datetime.utcnow(),
                LLMUsageLog.decision_relevant == False,
            )
            .all()
        )
        for content in expired:
            content.usage_log.content_deleted_at = datetime.utcnow()
            db.delete(content)

        db.commit()
        logger.info(f"Retención: {len(expired)} registros de contenido eliminados")
        return {"deleted_count": len(expired)}
    except Exception as e:
        db.rollback()
        logger.error(f"Error en política de retención: {e}")
        raise
    finally:
        db.close()

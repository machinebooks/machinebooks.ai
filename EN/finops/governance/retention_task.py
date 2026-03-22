# Source: The FinOps Engineer and the Machine -- Chapter 21
# Pattern: Data retention compliance task

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
    Daily task: deletes content from expired LLM interactions.
    - Interactions without decisional relevance: 90 days
    - decision_relevant interactions: preserved in LLMAuditRecord
    Complies with GDPR Art. 5(1)(e): storage limitation principle.
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
        logger.info(f"Retention: {len(expired)} content records deleted")
        return {"deleted_count": len(expired)}
    except Exception as e:
        db.rollback()
        logger.error(f"Error in retention policy: {e}")
        raise
    finally:
        db.close()

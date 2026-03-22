# Source: The FinOps Engineer and the Machine -- Chapter 22
# Pattern: Multi-provider failover service

# services/failover.py
from typing import Optional
from sqlalchemy.orm import Session
from models.llm_pricing import LLMModelPricing
import logging

logger = logging.getLogger(__name__)


def get_best_available_model(
    db: Session,
    task_type: str,
    min_context_tokens: int = 0,
    require_function_calling: bool = False,
) -> Optional[LLMModelPricing]:
    """
    Returns the best available model for a task.
    Considers health status, priority, capabilities, and cost.
    """
    query = db.query(LLMModelPricing).filter(
        LLMModelPricing.active == True,
        LLMModelPricing.health_status.in_(["healthy", "degraded"]),
    ).order_by(LLMModelPricing.priority)

    if min_context_tokens > 0:
        query = query.filter(
            LLMModelPricing.max_context_tokens >= min_context_tokens
        )
    if require_function_calling:
        query = query.filter(LLMModelPricing.supports_function_calling == True)

    candidates = query.all()

    # Exclude models not suitable for this specific task
    suitable = [
        m for m in candidates
        if not m.not_suitable_for_tasks
        or task_type not in m.not_suitable_for_tasks
    ]

    if not suitable:
        return candidates[0] if candidates else None

    # Prioritize models marked as suitable for this task
    preferred = [
        m for m in suitable
        if m.suitable_for_tasks and task_type in m.suitable_for_tasks
    ]
    return preferred[0] if preferred else suitable[0]

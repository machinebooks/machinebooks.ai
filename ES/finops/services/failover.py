# Extraído de: LibroFinOps/cap-22-multiproveedor.md
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
    Devuelve el mejor modelo disponible para una tarea.
    Considera estado de salud, prioridad, capacidades, y coste.
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

    # Excluir modelos no adecuados para esta tarea específica
    suitable = [
        m for m in candidates
        if not m.not_suitable_for_tasks
        or task_type not in m.not_suitable_for_tasks
    ]

    if not suitable:
        return candidates[0] if candidates else None

    # Priorizar modelos marcados como adecuados para esta tarea
    preferred = [
        m for m in suitable
        if m.suitable_for_tasks and task_type in m.suitable_for_tasks
    ]
    return preferred[0] if preferred else suitable[0]

# Extraído de: LibroFinOps/cap-04-instrumentacion-llm.md
# routers/llm_usage.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta, timezone
from ..models import LLMUsageLog
from ..database import get_async_session

router = APIRouter(prefix="/api/llm-usage", tags=["LLM Usage"])

@router.get("/summary")
async def get_usage_summary(
    days: int = Query(30, ge=1, le=365),
    service_name: str | None = Query(None),
    user_id: str | None = Query(None),
):
    """
    Resumen de consumo y coste por servicio y usuario.
    Endpoint principal para el dashboard de FinOps.
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)

    filters = [LLMUsageLog.timestamp >= since]
    if service_name:
        filters.append(LLMUsageLog.service_name == service_name)
    if user_id:
        filters.append(LLMUsageLog.user_id == user_id)

    async with get_async_session() as session:
        # Agrupación por servicio
        by_service = await session.execute(
            select(
                LLMUsageLog.service_name,
                LLMUsageLog.model,
                func.count().label("calls"),
                func.sum(LLMUsageLog.input_tokens).label("input_tokens"),
                func.sum(LLMUsageLog.output_tokens).label("output_tokens"),
                func.sum(LLMUsageLog.total_cost_usd).label("total_cost_usd"),
                func.avg(LLMUsageLog.latency_ms).label("avg_latency_ms"),
            )
            .where(and_(*filters))
            .group_by(LLMUsageLog.service_name, LLMUsageLog.model)
            .order_by(func.sum(LLMUsageLog.total_cost_usd).desc())
        )

        return {
            "period_days": days,
            "by_service": [dict(row._mapping) for row in by_service],
        }

# Extraído de: LibroFinOps/cap-06-atribucion.md
# routers/attribution.py
from fastapi import APIRouter, Query
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta, timezone
from ..models import LLMUsageLog, UserBudgetOverride
from ..database import get_async_session

router = APIRouter(prefix="/api/attribution", tags=["Attribution"])

@router.get("/user-ranking")
async def get_user_spending_ranking(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Ranking de usuarios por gasto LLM en el período.
    Incluye si el usuario tiene override de presupuesto activo.
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)

    async with get_async_session() as session:
        # Gasto por usuario
        usage_q = await session.execute(
            select(
                LLMUsageLog.user_id,
                func.count().label("total_calls"),
                func.sum(LLMUsageLog.total_tokens).label("total_tokens"),
                func.sum(LLMUsageLog.total_cost_usd).label("total_cost_usd"),
                func.avg(LLMUsageLog.total_cost_usd).label("avg_cost_per_call"),
            )
            .where(
                and_(
                    LLMUsageLog.timestamp >= since,
                    LLMUsageLog.user_id.isnot(None),
                )
            )
            .group_by(LLMUsageLog.user_id)
            .order_by(func.sum(LLMUsageLog.total_cost_usd).desc())
            .limit(limit)
        )
        users = [dict(row._mapping) for row in usage_q]

        # Enriquecer con información de overrides
        user_ids = [u["user_id"] for u in users]
        overrides_q = await session.execute(
            select(UserBudgetOverride).where(
                and_(
                    UserBudgetOverride.user_id.in_(user_ids),
                    UserBudgetOverride.is_active == True,
                )
            )
        )
        overrides_map = {o.user_id: o for o in overrides_q.scalars().all()}

        for user in users:
            uid = user["user_id"]
            if uid in overrides_map:
                override = overrides_map[uid]
                user["has_override"] = True
                user["override_budget_usd"] = override.budget_usd
                user["override_justification"] = override.justification
            else:
                user["has_override"] = False
                user["override_budget_usd"] = None

    return {
        "period_days": days,
        "users": users,
        "total_users_ranked": len(users),
    }


@router.get("/service-breakdown")
async def get_service_breakdown(days: int = Query(30, ge=1, le=365)):
    """
    Desglose del gasto por servicio y modelo.
    Permite identificar qué operación de negocio genera más coste.
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)

    async with get_async_session() as session:
        result = await session.execute(
            select(
                LLMUsageLog.service_name,
                LLMUsageLog.calling_app,
                LLMUsageLog.model,
                func.count().label("calls"),
                func.sum(LLMUsageLog.total_cost_usd).label("total_cost_usd"),
                func.sum(LLMUsageLog.total_tokens).label("total_tokens"),
                func.avg(LLMUsageLog.latency_ms).label("avg_latency_ms"),
            )
            .where(LLMUsageLog.timestamp >= since)
            .group_by(
                LLMUsageLog.service_name,
                LLMUsageLog.calling_app,
                LLMUsageLog.model,
            )
            .order_by(func.sum(LLMUsageLog.total_cost_usd).desc())
        )

        services = [dict(row._mapping) for row in result]

    # Calcular porcentaje sobre el total
    total_cost = sum(s["total_cost_usd"] for s in services)
    for service in services:
        service["cost_pct"] = (
            round(service["total_cost_usd"] / total_cost * 100, 1) if total_cost > 0 else 0.0
        )

    return {
        "period_days": days,
        "total_cost_usd": round(total_cost, 4),
        "services": services,
    }

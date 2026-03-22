# Source: The FinOps Engineer and the Machine -- Chapter 7
# Pattern: Budget status with burndown rate

# routers/budget_status.py
from fastapi import APIRouter
from datetime import datetime, timezone
from sqlalchemy import select, func, and_
from ..models import LLMUsageLog, BudgetConfig
from ..database import get_async_session

router = APIRouter(prefix="/api/budget-status")

@router.get("/current")
async def get_current_budget_status():
    """
    Budget traffic light: ok / warning / alert.
    Consumed by the admin panel banner
    and by the BudgetCheckMiddleware (Chapter 11).
    """
    now = datetime.now(timezone.utc)
    month_start = now.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    async with get_async_session() as session:
        spend = await session.execute(
            select(func.coalesce(
                func.sum(LLMUsageLog.total_cost_usd), 0.0
            )).where(LLMUsageLog.timestamp >= month_start)
        )
        current = float(spend.scalar())

        budget_row = await session.execute(
            select(BudgetConfig).where(and_(
                BudgetConfig.scope == "global",
                BudgetConfig.is_active == True,
            ))
        )
        budget = budget_row.scalar_one_or_none()

    if not budget:
        return {"status": "no_budget"}

    ratio = current / budget.budget_usd if budget.budget_usd > 0 else 0

    if ratio >= budget.block_threshold:
        status = "alert"
    elif ratio >= budget.alert_threshold:
        status = "warning"
    else:
        status = "ok"

    return {
        "status": status,
        "spend_usd": round(current, 4),
        "budget_usd": budget.budget_usd,
        "ratio_pct": round(ratio * 100, 1),
        "month": now.strftime("%Y-%m"),
    }

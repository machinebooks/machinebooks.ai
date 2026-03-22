# Extraído de: LibroFinOps/cap-01-la-factura.md
# routers/finops.py
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models.llm_usage_log import LLMUsageLog
from app.models.cloud_cost_daily import CloudCostDaily
from app.models.task_completion_log import TaskCompletionLog

router = APIRouter(prefix="/finops", tags=["finops"])

@router.get("/summary")
async def get_finops_summary(
    period_days: int = 30,
    db: Session = Depends(get_db),
):
    """Resumen unificado de costes y valor generado.
    Un endpoint, tres mundos, una verdad financiera."""
    since = datetime.utcnow() - timedelta(days=period_days)

    # Pilar 1: coste total en LLMs
    llm_costs = db.query(
        func.sum(LLMUsageLog.cost_total)
    ).filter(LLMUsageLog.created_at >= since).scalar() or 0.0

    # Pilar 2: coste cloud (agregación diaria cacheada)
    cloud_costs = db.query(
        func.sum(CloudCostDaily.cost_usd)
    ).filter(CloudCostDaily.date >= since.date()).scalar() or 0.0

    # Pilar 3: valor generado (ahorro acumulado)
    roi_savings = db.query(
        func.sum(TaskCompletionLog.money_saved_eur)
    ).filter(
        TaskCompletionLog.created_at >= since
    ).scalar() or 0.0

    total_cost = llm_costs + cloud_costs
    return {
        "period_days": period_days,
        "llm_cost_usd": round(llm_costs, 2),
        "cloud_cost_usd": round(cloud_costs, 2),
        "total_cost_usd": round(total_cost, 2),
        "roi_savings_eur": round(roi_savings, 2),
        "net_value_eur": round(
            roi_savings - (total_cost * 0.92), 2
        ),
    }

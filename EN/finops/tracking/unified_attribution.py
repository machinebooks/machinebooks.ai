# Source: The FinOps Engineer and the Machine -- Chapter 6
# Pattern: Unified attribution: LLM + cloud costs

# services/unified_attribution.py
from .aws_cost_categories import get_cost_by_category
from ..database import get_async_session
from ..models import LLMUsageLog
from sqlalchemy import select, func, and_
from datetime import datetime, timezone

async def get_service_total_cost(service_name: str, year: int, month: int) -> dict:
    """
    Total cost of a service: LLM API + cloud infrastructure.
    Unifies two data sources: LLMUsageLog (MySQL) + Cost Explorer (AWS).
    """
    # LLM cost from MySQL
    month_start = f"{year}-{month:02d}-01"
    if month == 12:
        month_end = f"{year + 1}-01-01"
    else:
        month_end = f"{year}-{month + 1:02d}-01"

    async with get_async_session() as session:
        llm_result = await session.execute(
            select(func.coalesce(func.sum(LLMUsageLog.total_cost_usd), 0.0))
            .where(
                and_(
                    LLMUsageLog.service_name == service_name,
                    LLMUsageLog.timestamp >= datetime(year, month, 1, tzinfo=timezone.utc),
                )
            )
        )
        llm_cost = float(llm_result.scalar())

    # Cloud cost from AWS Cost Explorer (by tag service=service_name)
    cloud_costs = get_cost_by_category(
        category_name="ByService",
        start_date=month_start,
        end_date=month_end,
    )
    cloud_cost = next(
        (c["cost_usd"] for c in cloud_costs if c["category_value"] == service_name),
        0.0,
    )

    total = llm_cost + cloud_cost

    return {
        "service": service_name,
        "period": f"{year}-{month:02d}",
        "llm_cost_usd": round(llm_cost, 4),
        "cloud_cost_usd": round(cloud_cost, 4),
        "total_cost_usd": round(total, 4),
        "llm_pct": round(llm_cost / total * 100, 1) if total > 0 else 0,
        "cloud_pct": round(cloud_cost / total * 100, 1) if total > 0 else 0,
    }

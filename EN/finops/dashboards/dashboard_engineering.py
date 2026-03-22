# Source: The FinOps Engineer and the Machine -- Chapter 7
# Pattern: Engineering-level dashboard endpoint

# routers/dashboard.py — Engineer level endpoint
from fastapi import APIRouter, Query
from sqlalchemy import select, func, text
from datetime import datetime, timedelta, timezone
from ..models import LLMUsageLog
from ..database import get_async_session

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/engineer")
async def get_engineer_metrics(hours: int = Query(24, ge=1, le=168)):
    """
    Technical metrics: tokens, latency, cache, errors.
    Window: last N hours. Update: every 60 seconds.
    """
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    async with get_async_session() as session:
        # Global KPIs for the period
        kpis = await session.execute(
            select(
                func.count().label("total_calls"),
                func.sum(LLMUsageLog.total_cost_usd).label("total_cost"),
                func.sum(LLMUsageLog.input_tokens).label("input_tokens"),
                func.sum(LLMUsageLog.output_tokens).label("output_tokens"),
                func.sum(LLMUsageLog.cache_read_tokens).label("cache_read"),
                func.avg(LLMUsageLog.latency_ms).label("avg_latency"),
            ).where(LLMUsageLog.timestamp >= since)
        )
        row = kpis.one()

        # Per-model breakdown for bar chart
        by_model = await session.execute(
            select(
                LLMUsageLog.model,
                func.count().label("calls"),
                func.sum(LLMUsageLog.total_cost_usd).label("cost_usd"),
            )
            .where(LLMUsageLog.timestamp >= since)
            .group_by(LLMUsageLog.model)
            .order_by(func.sum(LLMUsageLog.total_cost_usd).desc())
        )

    # Cache hit rate calculation
    cache_rate = (
        (row.cache_read or 0) / max((row.input_tokens or 1), 1) * 100
    )

    return {
        "window_hours": hours,
        "kpis": {
            "total_calls": row.total_calls or 0,
            "total_cost_usd": round(row.total_cost or 0, 4),
            "cache_hit_rate_pct": round(cache_rate, 1),
            "avg_latency_ms": round(row.avg_latency or 0, 0),
        },
        "by_model": [dict(r._mapping) for r in by_model],
    }

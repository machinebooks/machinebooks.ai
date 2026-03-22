# Extraído de: LibroFinOps/cap-07-dashboards.md
# routers/dashboard.py — Endpoint del nivel de dirección
@router.get("/cfo")
async def get_cfo_metrics(months: int = Query(6, ge=1, le=24)):
    """
    Tendencia mensual en EUR para dirección.
    Sin mencionar tokens ni modelos: vocabulario de negocio.
    """
    USD_TO_EUR = 0.92  # Factor configurable, ideal desde BD
    since = datetime.now(timezone.utc) - timedelta(days=months * 30)

    async with get_async_session() as session:
        monthly = await session.execute(
            select(
                func.date_format(
                    LLMUsageLog.timestamp, "%Y-%m"
                ).label("month"),
                func.sum(LLMUsageLog.total_cost_usd).label("cost_usd"),
                func.count(
                    LLMUsageLog.user_id.distinct()
                ).label("active_users"),
            )
            .where(LLMUsageLog.timestamp >= since)
            .group_by(text("month"))
            .order_by(text("month"))
        )
        data = []
        for row in monthly:
            cost_eur = row.cost_usd * USD_TO_EUR
            data.append({
                "month": row.month,
                "cost_eur": round(cost_eur, 2),
                "active_users": row.active_users,
                "cost_per_user_eur": round(
                    cost_eur / max(row.active_users, 1), 2
                ),
            })

    # Proyección lineal del mes actual
    projection = None
    current = next(
        (m for m in data
         if m["month"] == datetime.now().strftime("%Y-%m")),
        None,
    )
    if current:
        day = datetime.now().day
        projection = round(current["cost_eur"] / day * 30, 2)

    return {
        "currency": "EUR",
        "monthly_trend": data,
        "projection_eur": projection,
    }

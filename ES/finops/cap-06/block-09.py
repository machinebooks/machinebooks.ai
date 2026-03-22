# Extraído de: LibroFinOps/cap-06-atribucion.md
@router.get("/budgets/status")
async def get_all_budgets_status():
    """
    Estado actual de todos los presupuestos activos.
    Incluye gasto acumulado y porcentaje consumido del período.
    """
    period_key = datetime.now(timezone.utc).strftime("%Y-%m")

    async with get_async_session() as session:
        # Cargar todos los presupuestos activos
        budgets_q = await session.execute(
            select(BudgetConfig).where(BudgetConfig.is_active == True)
        )
        budgets = budgets_q.scalars().all()

        # Cargar los contadores acumulados del período actual
        counters_q = await session.execute(
            select(BudgetCounter).where(
                BudgetCounter.period_key == period_key
            )
        )
        counters = {
            (c.scope, c.scope_id): c
            for c in counters_q.scalars().all()
        }

        # Cargar overrides activos
        overrides_q = await session.execute(
            select(UserBudgetOverride).where(
                UserBudgetOverride.is_active == True
            )
        )
        overrides = overrides_q.scalars().all()

    result = []
    for budget in budgets:
        counter = counters.get((budget.scope, budget.scope_id))
        accumulated = counter.accumulated_usd if counter else 0.0
        ratio = accumulated / budget.budget_usd if budget.budget_usd > 0 else 0

        status = (
            "blocked" if ratio >= budget.block_threshold
            else "warning" if ratio >= budget.alert_threshold
            else "ok"
        )

        result.append({
            "scope": budget.scope,
            "scope_id": budget.scope_id,
            "budget_usd": budget.budget_usd,
            "accumulated_usd": round(accumulated, 4),
            "ratio_pct": round(ratio * 100, 1),
            "status": status,
            "remaining_usd": round(
                max(0, budget.budget_usd - accumulated), 4
            ),
        })

    # Añadir los overrides de usuario como entradas adicionales
    for override in overrides:
        counter = counters.get(("user", override.user_id))
        accumulated = counter.accumulated_usd if counter else 0.0
        ratio = accumulated / override.budget_usd if override.budget_usd > 0 else 0
        result.append({
            "scope": "user_override",
            "scope_id": override.user_id,
            "budget_usd": override.budget_usd,
            "accumulated_usd": round(accumulated, 4),
            "ratio_pct": round(ratio * 100, 1),
            "status": "ok" if ratio < 0.8 else "warning" if ratio < 1.0 else "blocked",
            "justification": override.justification,
            "review_date": override.review_date.isoformat(),
        })

    return {
        "period": period_key,
        "budgets": sorted(result, key=lambda x: x["ratio_pct"], reverse=True),
    }

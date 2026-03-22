# Extraído de: LibroFinOps/cap-06-atribucion.md
# En el método _persist_log del LLMUsageTracker
async def _update_budget_counters(
    session, cost_usd: float, user_id: str | None,
    service_name: str, period_key: str
) -> None:
    """
    Actualiza los contadores acumulados de presupuesto.
    Usa upsert para evitar condiciones de carrera con múltiples workers.
    """
    scopes_to_update = [
        ("global", None),
        ("service", service_name),
    ]
    if user_id:
        scopes_to_update.append(("user", user_id))

    for scope, scope_id in scopes_to_update:
        await session.execute(
            text("""
                INSERT INTO budget_counters (id, scope, scope_id, period_key, accumulated_usd, call_count)
                VALUES (:id, :scope, :scope_id, :period_key, :cost, 1)
                ON DUPLICATE KEY UPDATE
                    accumulated_usd = accumulated_usd + :cost,
                    call_count = call_count + 1,
                    last_updated = NOW()
            """),
            {
                "id": str(uuid.uuid4()),
                "scope": scope,
                "scope_id": scope_id,
                "period_key": period_key,
                "cost": cost_usd,
            },
        )

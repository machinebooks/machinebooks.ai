# Extraído de: LibroAIGateway/cap-13-tenants-cuotas.md
# Firma simplificada
async def check_and_consume(
    db, device_id, user_id, org_id,
    multiplier: float = 0,
    *,
    estimated_cost_eur: float | None = None,
    pack_slug: str | None = None,
) -> dict:
    # 1. Guardrails organizativos (hard — no overage)
    if org_spent + amount > org_budget:
        return {"allowed": False, "bucket_hit": "organization_monthly", ...}

    # 2. Guardrails de equipo pooled y area (hard)
    if team_spent + amount > team_budget:
        return {"allowed": False, "bucket_hit": "team_monthly", ...}

    # 3. Cuotas personales (con overage)
    for bucket in ACTIVE_BUCKETS:
        q = await _get_or_create_quota(..., lock=True)
        if q.used + amount > q.entitlement:
            if q.overage_permitted:
                continue  # Permite sobregiro
            return {"allowed": False, "bucket_hit": bucket, ...}

    # 4. Todos OK → reservar
    for q in quotas:
        q.used += amount
    await db.commit()
    return {"allowed": True, ...}

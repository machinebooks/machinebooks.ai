# Extracted from: LibroAIGateway/cap-13-tenants-quotas.md
async def reconcile_eur_reservation(
    db, device_id, user_id, org_id,
    *, estimated_cost_eur, actual_cost_eur, pack_slug=None,
):
    estimate = Decimal(str(estimated_cost_eur or 0))
    actual   = Decimal(str(actual_cost_eur or 0))
    delta = actual - estimate
    if abs(delta) < Decimal("0.000001"):
        return  # Insignificant difference

    # Adjust used in all active buckets
    for bucket in ACTIVE_BUCKETS:
        q = await _get_or_create_quota(..., lock=True)
        q.used = max(Decimal("0"), q.used + delta)
    await db.commit()

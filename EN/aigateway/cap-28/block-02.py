# Extracted from: LibroAIGateway/cap-28-admin-operations-ai.md
# gateway/app/api/v1/admin/dashboard.py:30-53 (synthetic)
@router.get("/stats")
async def get_stats(
    period_hours: int = 24,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_viewer),
):
    since = datetime.utcnow() - timedelta(hours=period_hours)
    base = select(AuditLog).where(AuditLog.created_at >= since)
    base = _apply_org_filter(base, AuditLog, current_user)  # multi-tenant

    # Totals: requests, tokens, cost, average latency excluding outliers
    totals_q = select(
        func.count(AuditLog.id).label("total_requests"),
        func.sum(AuditLog.prompt_tokens + AuditLog.completion_tokens).label("total_tokens"),
        func.sum(AuditLog.cost_usd).label("total_cost"),
    ).where(AuditLog.status == "success")
    totals_q = _apply_org_filter(totals_q, AuditLog, current_user)
    row = (await db.execute(totals_q)).one()
    # ... distribution by model, provider, active devices

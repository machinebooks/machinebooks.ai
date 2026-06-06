# Extraído de: LibroAIGateway/cap-23-compliance-regulatorio.md
# gateway/app/api/v1/admin/compliance.py:40-128 (extracto)
@router.get("/moderation-report")
async def get_moderation_report(
    period_start: Optional[str] = Query(None, description="YYYY-MM-DD"),
    period_end:   Optional[str] = Query(None, description="YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    """Genera reporte de moderación para DSA compliance."""
    conds = []
    if period_start:
        conds.append(ModerationAction.created_at >= period_start)
    if period_end:
        conds.append(ModerationAction.created_at <= period_end)
    where_clause = and_(*conds) if conds else True

    # Breakdown por categoría, acción tomada y severidad
    blocked = func.sum(case((ModerationAction.action_taken == "block", 1), else_=0))
    flagged = func.sum(case((ModerationAction.action_taken == "flag", 1), else_=0))
    # ... agrupación y retorno (ver código fuente completo)

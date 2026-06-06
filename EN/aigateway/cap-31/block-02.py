# Extracted from: LibroAIGateway/cap-31-adoption-compliance-portal.md
# Published cases, filterable, with i18n — gateway/app/api/v1/use_cases.py:31-67
@router.get("")
async def list_use_cases(
    role: Optional[str] = Query(None, max_length=60),
    app: Optional[str] = Query(None, max_length=24),
    mechanism: Optional[str] = Query(None, max_length=20),
    tag: Optional[str] = Query(None, max_length=60),
    sort: str = Query("popular", pattern="^(popular|recent)$"),
    locale: str = Query("es", pattern="^(es|en)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(AIPrompt).where(
        AIPrompt.kind == "use_case",
        AIPrompt.is_active == True,
    )
    if role:
        stmt = stmt.where(AIPrompt.target_role == role)
    # ... similar filters for app, mechanism, tag ...

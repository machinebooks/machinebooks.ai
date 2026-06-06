# Extraído de: LibroAIGateway/cap-22-governance-engine.md
query = select(PIIRule).where(PIIRule.is_active == True)
if organization_id is not None:
    query = query.where(
        or_(
            PIIRule.organization_id.is_(None),
            PIIRule.organization_id == organization_id,
        )
    )

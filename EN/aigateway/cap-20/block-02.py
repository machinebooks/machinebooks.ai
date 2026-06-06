# Extracted from: LibroAIGateway/cap-20-classification-guardrails-firewall.md
# gateway/app/services/content_classifier_service.py:47-58

@classmethod
async def load_categories(cls, db: AsyncSession, org_id: int | None = None) -> list[dict]:
    """Loads active categories from DB (with in-memory cache)."""
    global _categories_cache
    if _categories_cache is not None:
        return _categories_cache

    query = select(ContentCategory).where(ContentCategory.is_active == True)
    result = await db.execute(query)
    categories = result.scalars().all()
    _categories_cache = [c.to_dict() for c in categories]
    return _categories_cache

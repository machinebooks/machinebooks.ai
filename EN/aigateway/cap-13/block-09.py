# Extracted from: LibroAIGateway/cap-13-tenants-quotas.md
class PlanEntitlementService:
    _cache: Optional[dict] = None

    @classmethod
    async def get_entitlements(cls, db, plan: str) -> dict[str, float]:
        if cls._cache is None:
            await cls._load(db)
        # Safe fallback: if the plan does not exist in DB, use "free"
        base = FALLBACK_ENTITLEMENTS.get(plan) or FALLBACK_ENTITLEMENTS["free"]
        overrides = (cls._cache or {}).get(plan) or {}
        base.update(overrides)
        return base

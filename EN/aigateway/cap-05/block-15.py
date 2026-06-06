# Extracted from: LibroAIGateway/cap-05-router-smart-select.md
@classmethod
async def filter_models_by_residency(cls, db, org_id, models) -> list[dict]:
    org = await cls._get_org(db, org_id)
    allowed = cls._parse_json_field(getattr(org, "allowed_providers", None))
    if allowed is None:
        return models
    return [m for m in models if m.get("provider") in allowed]

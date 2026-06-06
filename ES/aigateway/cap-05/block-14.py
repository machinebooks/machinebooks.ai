# Extraído de: LibroAIGateway/cap-05-router-smart-select.md
@classmethod
async def check_region_allowed(cls, db, org_id, region) -> dict:
    org = await cls._get_org(db, org_id)
    blocked = cls._parse_json_field(getattr(org, "blocked_regions", None))
    if blocked is None:
        return {"allowed": True, "reason": "Sin restricción de regiones"}
    if region in blocked:
        return {"allowed": False,
                "reason": f"Región {region} bloqueada para esta organización"}
    return {"allowed": True, "reason": f"Región {region} permitida"}

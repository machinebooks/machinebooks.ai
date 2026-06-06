# Extracted from: LibroAIGateway/cap-05-router-smart-select.md
@classmethod
async def check_region_allowed(cls, db, org_id, region) -> dict:
    org = await cls._get_org(db, org_id)
    blocked = cls._parse_json_field(getattr(org, "blocked_regions", None))
    if blocked is None:
        return {"allowed": True, "reason": "No region restriction"}
    if region in blocked:
        return {"allowed": False,
                "reason": f"Region {region} blocked for this organization"}
    return {"allowed": True, "reason": f"Region {region} allowed"}

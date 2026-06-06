# Extracted from: LibroAIGateway/cap-02-mental-model-tenancy.md
async def get_tenant_from_request(
    request: Request, db: AsyncSession
) -> Organization:
    # 1. User API key (upstream middleware)
    uak = getattr(request.state, "user_api_key_user", None)
    if uak and getattr(uak, "organization_id", None):
        return await _resolve_org(uak.organization_id, db)

    # 2. Application or synthetic override
    override = getattr(request.state, "device_id_override", None)
    if override:
        org_id = await _org_from_device_id(override, db)
        if org_id:
            return await _resolve_org(org_id, db)

    # 3. Legacy API key (api_keys table)
    # 4. Explicit header (super-admin only)
    org_header = request.headers.get("X-Organization-ID")
    # ...

    # 5. JWT claims
    # 6. Service JWT with device_id
    # 7. X-Device-ID header
    # ...
    return None  # → 401

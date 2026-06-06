# Extraído de: LibroAIGateway/cap-02-modelo-mental-tenancy.md
async def get_tenant_from_request(
    request: Request, db: AsyncSession
) -> Organization:
    # 1. API key de usuario (middleware upstream)
    uak = getattr(request.state, "user_api_key_user", None)
    if uak and getattr(uak, "organization_id", None):
        return await _resolve_org(uak.organization_id, db)

    # 2. Application o override sintético
    override = getattr(request.state, "device_id_override", None)
    if override:
        org_id = await _org_from_device_id(override, db)
        if org_id:
            return await _resolve_org(org_id, db)

    # 3. API key legacy (tabla api_keys)
    # 4. Header explícito (solo super-admin)
    org_header = request.headers.get("X-Organization-ID")
    # ...

    # 5. JWT claims
    # 6. JWT service con device_id
    # 7. Header X-Device-ID
    # ...
    return None  # → 401

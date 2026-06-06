# Extracted from: LibroAIGateway/cap-13-tenants-quotas.md
# Tenant resolution chain (simplified)
async def get_tenant_from_request(request, db) -> Organization:
    # 1. Personal API key (n7x-API-*) → owner user's org
    uak_user = getattr(request.state, "user_api_key_user", None)
    if uak_user and uak_user.organization_id:
        return await _org_by_id(db, uak_user.organization_id)

    # 2. Application key (n7x-app-*) → synthetic device's org
    if request.state.device_id_override:
        return await _org_from_device(db, request.state.device_id_override)

    # 3. Legacy API key (SHA-256 hash)
    if auth_header.startswith("Bearer n7x-"):
        return await _tenant_from_api_key(key, db)

    # 4. JWT claims: explicit org_id (or X-Organization-ID for super-admins)
    payload = decode_token(token)
    if payload and payload.get("org_id"):
        return await _org_by_id(db, payload["org_id"])

    # 5. Fallback: X-Device-ID header
    device_id = request.headers.get("X-Device-ID")
    return await _org_from_device(db, device_id)

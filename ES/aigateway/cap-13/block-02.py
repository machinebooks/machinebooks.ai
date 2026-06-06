# Extraído de: LibroAIGateway/cap-13-tenants-cuotas.md
# Las API keys legacy se buscan por hash SHA-256, nunca por texto plano.
async def _tenant_from_api_key(key: str, db) -> Organization:
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    api_key = await db.scalar(select(ApiKey).where(
        ApiKey.key_hash == key_hash,
        ApiKey.is_active == True,
    ))
    if not api_key:
        raise HTTPException(401, "API key inválida")

    # Actualizamos last_used (auditoría)
    await db.execute(
        text("UPDATE api_keys SET last_used_at = NOW() WHERE id = :id"),
        {"id": api_key.id},
    )
    return await _org_by_id(db, api_key.organization_id)

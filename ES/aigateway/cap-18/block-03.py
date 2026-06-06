# Extraído de: LibroAIGateway/cap-18-keys-cifrado-master.md
# Rotación dual (gateway/app/services/user_api_key_service.py)
async def rotate(db: AsyncSession, key_id: int, grace_hours: int = 24) -> tuple[UserApiKey, str]:
    key = <buscar clave activa por key_id>
    if key is None:
        raise UserApiKeyError("Token no encontrado o no activo")

    # 1. La primaria actual pasa a secundaria con expiración grace
    key.secondary_key_hash = key.key_hash
    key.secondary_key_prefix = key.key_prefix
    key.secondary_expires_at = datetime.utcnow() + timedelta(hours=grace_hours)

    # 2. Nueva primaria generada
    raw_key, prefix = _generate_raw_key(key.slug)
    key.key_hash = _hash_token(raw_key)
    key.key_prefix = prefix
    await db.commit()
    return key, raw_key

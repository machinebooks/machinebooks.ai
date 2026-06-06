# Extracted from: LibroAIGateway/cap-18-keys-encryption-master.md
# Dual rotation (gateway/app/services/user_api_key_service.py)
async def rotate(db: AsyncSession, key_id: int, grace_hours: int = 24) -> tuple[UserApiKey, str]:
    key = <look up active key by key_id>
    if key is None:
        raise UserApiKeyError("Token not found or not active")

    # 1. Current primary moves to secondary with grace expiration
    key.secondary_key_hash = key.key_hash
    key.secondary_key_prefix = key.key_prefix
    key.secondary_expires_at = datetime.utcnow() + timedelta(hours=grace_hours)

    # 2. New primary generated
    raw_key, prefix = _generate_raw_key(key.slug)
    key.key_hash = _hash_token(raw_key)
    key.key_prefix = prefix
    await db.commit()
    return key, raw_key

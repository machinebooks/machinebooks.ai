# Extracted from: LibroAIGateway/cap-18-keys-encryption-master.md
# Bearer validation (gateway/app/services/user_api_key_service.py)
async def validate_bearer(db: AsyncSession, raw_token: str) -> Optional[UserApiKey]:
    if not raw_token or not raw_token.startswith("n7x-API-"):
        return None
    token_hash = _hash_token(raw_token)
    now = datetime.utcnow()

    result = await db.execute(
        select(UserApiKey).where(
            UserApiKey.status == "active",
            UserApiKey.deleted_at.is_(None),
            or_(UserApiKey.expires_at.is_(None), UserApiKey.expires_at > now),
            or_(
                UserApiKey.key_hash == token_hash,                    # primary
                and_(
                    UserApiKey.secondary_key_hash == token_hash,      # secondary
                    or_(
                        UserApiKey.secondary_expires_at.is_(None),
                        UserApiKey.secondary_expires_at > now,
                    ),
                ),
            ),
        ).limit(1)
    )
    return result.scalar_one_or_none()

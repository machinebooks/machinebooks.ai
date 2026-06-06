# Extracted from: LibroAIGateway/cap-30-user-portal.md
# gateway/app/api/v1/me_api_keys.py — dual-key rotation
@router.post("/{key_id}/rotate")
async def rotate_api_key(key_id: int, current_user, db):
    key, raw_token = await UserApiKeyService.rotate(db, key_id=key_id)
    return {
        "data": {
            "token": raw_token,
            "key_prefix": key.key_prefix,
            "expires_at": key.expires_at.isoformat(),
            "secondary_expires_at": key.secondary_expires_at.isoformat(),
        },
        "message": "Token rotated. Previous key valid for 24h.",
    }

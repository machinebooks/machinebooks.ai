# Extracted from: LibroAIGateway/cap-30-user-portal.md
# gateway/app/api/v1/me_api_keys.py — create key
@router.post("")
async def create_api_key(body: ApiKeyCreate, current_user, db):
    expires = body.expires_in_days or DEFAULT_EXPIRES_IN_DAYS  # 90
    key, raw_token = await UserApiKeyService.create(
        db, user_id=current_user.id, slug=body.app_slug,
        name=body.display_name, expires_in_days=expires,
    )
    return {
        "data": {
            "token": raw_token,  # Only visible once
            "app_slug": key.slug, "display_name": key.name,
            "expires_at": key.expires_at.isoformat(),
        },
        "message": "Token created. Save it now: it will not be shown again.",
    }

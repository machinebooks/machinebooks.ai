# Extraído de: LibroAIGateway/cap-16-jwt-device-binding.md
# Fail-closed en revocación (gateway/app/core/security.py:219-246)
async def check_token_revoked(payload: dict) -> bool:
    try:
        redis = await get_redis()
        jti = payload.get("jti", "")
        sub = payload.get("sub", "")
        device_id = payload.get("device_id", "")
        iat = payload.get("iat", 0)
        user_id = int(sub) if sub and str(sub).isdigit() else 0
        return await SessionService.check_all(
            redis, jti, user_id, device_id or None, float(iat)
        )
    except Exception as exc:
        logger.error(
            "check_token_revoked:redis_failed err=%s — fail-closed", exc
        )
        return True  # Redis caído ⇒ considerar revocado ⇒ DENEGAR

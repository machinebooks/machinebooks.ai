# Extracted from: LibroAIGateway/cap-17-sso-scim-mfa.md
# gateway/app/services/mfa_service.py — verification with atomic rate limit
@classmethod
async def verify_code(cls, redis, user_id: int, code: str) -> dict:
    key = f"mfa:{user_id}"
    if not await redis.exists(key):
        return {"valid": False, "reason": "expired"}

    # INCR-FIRST: we increment before comparing (anti race condition)
    new_attempts = await redis.hincrby(key, "attempts", 1)
    if int(new_attempts) > 5:
        await redis.delete(key)
        return {"valid": False, "reason": "max_attempts"}

    stored_code = await redis.hget(key, "code") or ""
    if not secrets.compare_digest(code.strip(), stored_code):
        return {"valid": False, "reason": "invalid_code"}

    await redis.delete(key)  # single-use
    return {"valid": True, "reason": "ok"}

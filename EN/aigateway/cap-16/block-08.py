# Extracted from: LibroAIGateway/cap-16-jwt-device-binding.md
# SessionService — revocation via Redis blacklist
BLACKLIST_PREFIX = "tkbl:"        # token blacklist by individual JTI
USER_REVOKE_PREFIX = "urev:"      # revocation at user level
DEVICE_REVOKE_PREFIX = "drev:"    # revocation at device level
MAX_TOKEN_LIFETIME = 30 * 24 * 3600  # 30 days in seconds

class SessionService:
    @classmethod
    async def revoke_token(cls, redis, jti: str) -> None:
        await redis.set(f"tkbl:{jti}", "1", ex=MAX_TOKEN_LIFETIME)

    @classmethod
    async def revoke_user(cls, redis, user_id: int) -> None:
        await redis.set(f"urev:{user_id}",
                        datetime.utcnow().isoformat(),
                        ex=MAX_TOKEN_LIFETIME)

    @classmethod
    async def revoke_device(cls, redis, device_id: str) -> None:
        await redis.set(f"drev:{device_id}",
                        datetime.utcnow().isoformat(),
                        ex=MAX_TOKEN_LIFETIME)

# Extraído de: LibroAIGateway/cap-16-jwt-device-binding.md
# SessionService — revocación vía Redis blacklist
BLACKLIST_PREFIX = "tkbl:"        # token blacklist por JTI individual
USER_REVOKE_PREFIX = "urev:"      # revocación a nivel usuario
DEVICE_REVOKE_PREFIX = "drev:"    # revocación a nivel dispositivo
MAX_TOKEN_LIFETIME = 30 * 24 * 3600  # 30 días en segundos

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

# Extracted from: LibroAIGateway/cap-16-jwt-device-binding.md
# Complete verification: JTI + user + device (gateway/app/services/session_service.py)
@classmethod
async def check_all(cls, redis, jti: str, user_id: int,
                    device_id: str | None, iat: float) -> bool:
    if await cls.is_token_revoked(redis, jti):
        return True                      # Individual JTI blacklist
    if await cls.is_user_revoked(redis, user_id, iat):
        return True                      # User revoked AFTER token issued
    if device_id and await cls.is_device_revoked(redis, device_id, iat):
        return True                      # Device revoked AFTER token issued
    return False

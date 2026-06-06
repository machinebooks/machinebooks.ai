# Extracted from: LibroAIGateway/cap-16-jwt-device-binding.md
# Issuance with device binding (gateway/app/core/security.py)
def create_access_token(
    user_id: int,
    role: str,
    device_id: str | None = None,
    organization_id: int | None = None,
    is_super_admin: bool = False,
) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "jti": str(uuid.uuid4()),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    if device_id:
        payload["device_id"] = device_id
    if organization_id is not None:
        payload["org_id"] = organization_id
    if is_super_admin:
        payload["super"] = True
    return jwt.encode(payload, settings.JWT_SECRET_KEY,
                       algorithm=settings.JWT_ALGORITHM)

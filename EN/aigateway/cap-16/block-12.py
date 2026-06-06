# Extracted from: LibroAIGateway/cap-16-jwt-device-binding.md
# Refresh token rotation (gateway/app/core/security.py:121-148)
def create_refresh_token(
    user_id: int,
    client_fingerprint: str | None = None,
    family_id: str | None = None,
) -> tuple[str, str, str]:
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    jti = str(uuid.uuid4())
    fam = family_id or str(uuid.uuid4())
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": jti,
        "family_id": fam,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    if client_fingerprint:
        payload["cfp"] = client_fingerprint  # fingerprint for session pinning
    token = jwt.encode(payload, settings.JWT_SECRET_KEY,
                       algorithm=settings.JWT_ALGORITHM)
    return token, jti, fam

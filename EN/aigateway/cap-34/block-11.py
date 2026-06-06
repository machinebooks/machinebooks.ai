# Extracted from: LibroAIGateway/cap-34-celery-deployment-config.md
@field_validator("JWT_SECRET_KEY", "GATEWAY_SECRET_KEY")
@classmethod
def secret_must_be_strong(cls, v: str, info) -> str:
    forbidden = ["change-me", "changeme", "default", "secret-key", "your-secret"]
    lowered = v.lower()
    if any(token in lowered for token in forbidden):
        if is_prod:
            raise ValueError(f"{info.field_name} contains a placeholder.")
        _settings_logger.warning("Secret placeholder detected.")
    if len(v) < 32 and is_prod:
        raise ValueError(f"Must be at least 32 characters (current: {len(v)}).")

# Extraído de: LibroAIGateway/cap-34-celery-deployment-config.md
@field_validator("JWT_SECRET_KEY", "GATEWAY_SECRET_KEY")
@classmethod
def secret_must_be_strong(cls, v: str, info) -> str:
    forbidden = ["change-me", "changeme", "default", "secret-key", "your-secret"]
    lowered = v.lower()
    if any(token in lowered for token in forbidden):
        if is_prod:
            raise ValueError(f"{info.field_name} contiene un placeholder.")
        _settings_logger.warning("Secret placeholder detectado.")
    if len(v) < 32 and is_prod:
        raise ValueError(f"Debe tener al menos 32 caracteres (actual: {len(v)}).")

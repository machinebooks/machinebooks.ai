# Extracted from: LibroAIGateway/cap-34-celery-deployment-config.md
@field_validator("CORS_ORIGINS")
@classmethod
def cors_origins_no_wildcard_in_production(cls, v: List[str]) -> List[str]:
    env = os.environ.get("GATEWAY_ENV", "development").lower()
    if env != "production":
        return v
    for origin in v:
        o = (origin or "").strip().lower()
        if o == "*" or "localhost" in o or "127.0.0.1" in o:
            raise ValueError("CORS_ORIGINS cannot contain wildcards/localhost in production.")
    return v

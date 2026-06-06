# Extraído de: LibroAIGateway/cap-23-compliance-regulatorio.md
# gateway/app/services/dpo_service.py:26-32
SALT = os.environ.get("N7X_PSEUDONYM_SALT")
if not SALT or len(SALT) < 32:
    if os.environ.get("GATEWAY_ENV", "development") == "production":
        raise RuntimeError(
            "N7X_PSEUDONYM_SALT requerida en produccion (>=32 chars)."
        )

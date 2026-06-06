# Extracted from: LibroAIGateway/cap-18-keys-encryption-master.md
# Master key resolution (gateway/app/core/crypto.py:43-69)
def _get_master_key() -> bytes:
    key_hex = os.environ.get("N7X_MASTER_KEY", "")
    if not key_hex:
        # Ephemeral key in dev — warning, DO NOT use in production
        if _DEV_EPHEMERAL_KEY is None:
            _DEV_EPHEMERAL_KEY = secrets.token_bytes(32)
            logger.warning("N7X_MASTER_KEY not configured — EPHEMERAL key")
        return _DEV_EPHEMERAL_KEY
    if len(key_hex) != 64:
        raise ValueError(f"N7X_MASTER_KEY must be 64 hex chars (32 bytes)")
    return bytes.fromhex(key_hex)

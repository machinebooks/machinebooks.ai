# Extraído de: LibroAIGateway/cap-18-keys-cifrado-master.md
# Resolución de master key (gateway/app/core/crypto.py:43-69)
def _get_master_key() -> bytes:
    key_hex = os.environ.get("N7X_MASTER_KEY", "")
    if not key_hex:
        # Clave efímera en dev — warning, NO usar en producción
        if _DEV_EPHEMERAL_KEY is None:
            _DEV_EPHEMERAL_KEY = secrets.token_bytes(32)
            logger.warning("N7X_MASTER_KEY no configurada — clave EFIMERA")
        return _DEV_EPHEMERAL_KEY
    if len(key_hex) != 64:
        raise ValueError(f"N7X_MASTER_KEY debe tener 64 chars hex (32 bytes)")
    return bytes.fromhex(key_hex)

# Extraído de: LibroAIGateway/cap-18-keys-cifrado-master.md
# Generación de clave opaca (gateway/app/services/user_api_key_service.py)
def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def _generate_raw_key(slug: str) -> tuple[str, str]:
    """Genera bearer n7x-API-{slug}-{32 hex} + prefix para listado."""
    secret = secrets.token_hex(16)           # 32 caracteres hex = 128 bits
    raw = f"n7x-API-{slug}-{secret}"       # ej: n7x-API-cli-d8e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5
    prefix = raw[:32]                        # "n7x-API-cli-d8e1f2a3b4c5d"
    return raw, prefix

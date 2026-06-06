# Extraído de: LibroAIGateway/cap-21-audit-append-only.md
@classmethod
def encrypt(cls, payload: dict) -> tuple[bytes, bytes]:
    plaintext = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    nonce = secrets.token_bytes(12)           # 96 bits, único
    ct = AESGCM(cls._key).encrypt(nonce, plaintext, None)
    return ct, nonce

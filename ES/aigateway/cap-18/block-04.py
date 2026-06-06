# Extraído de: LibroAIGateway/cap-18-keys-cifrado-master.md
# Cifrado en reposo de campos sensibles (gateway/app/core/crypto.py)
def encrypt_field(plaintext: str | None) -> str | None:
    if not plaintext or plaintext.startswith("enc:"):
        return plaintext  # None, vacío o ya cifrado → no tocar

    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    nonce = os.urandom(12)                            # 96 bits para AES-GCM
    key = _master_key_for_version("v1")               # N7X_MASTER_KEY
    ct = AESGCM(key).encrypt(nonce, plaintext.encode("utf-8"), None)
    return "enc:v1:" + base64.b64encode(nonce + ct).decode("ascii")

def decrypt_field(value: str | None) -> str | None:
    if not value or not value.startswith("enc:"):
        return value  # texto plano — backward compat
    # Detecta versión: "enc:v1:<b64>" o "enc:<b64>" (legacy)
    # Descifra con la master key correspondiente a la versión

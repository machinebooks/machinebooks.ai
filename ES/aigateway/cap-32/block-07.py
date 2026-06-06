# Extraído de: LibroAIGateway/cap-32-modelo-de-datos.md
def encrypt_field(plaintext: str | None) -> str | None:
    """Cifra un string con AES-256-GCM.
    Formato: "enc:v1:<base64(nonce[12] + ct)>"
    """
    if not plaintext or plaintext.startswith("enc:"):
        return plaintext
    nonce = os.urandom(12)  # 96 bits — recomendado para AES-GCM
    key = _master_key_for_version("v1")
    ct = AESGCM(key).encrypt(nonce, plaintext.encode("utf-8"), None)
    return "enc:v1:" + base64.b64encode(nonce + ct).decode("ascii")

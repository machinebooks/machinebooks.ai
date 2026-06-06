# Extracted from: LibroAIGateway/cap-32-data-model.md
def encrypt_field(plaintext: str | None) -> str | None:
    """Encrypts a string with AES-256-GCM.
    Format: "enc:v1:<base64(nonce[12] + ct)>"
    """
    if not plaintext or plaintext.startswith("enc:"):
        return plaintext
    nonce = os.urandom(12)  # 96 bits — recommended for AES-GCM
    key = _master_key_for_version("v1")
    ct = AESGCM(key).encrypt(nonce, plaintext.encode("utf-8"), None)
    return "enc:v1:" + base64.b64encode(nonce + ct).decode("ascii")

# Extracted from: LibroAIGateway/cap-18-keys-encryption-master.md
# Encryption at rest for sensitive fields (gateway/app/core/crypto.py)
def encrypt_field(plaintext: str | None) -> str | None:
    if not plaintext or plaintext.startswith("enc:"):
        return plaintext  # None, empty, or already encrypted → leave alone

    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    nonce = os.urandom(12)                            # 96 bits for AES-GCM
    key = _master_key_for_version("v1")               # N7X_MASTER_KEY
    ct = AESGCM(key).encrypt(nonce, plaintext.encode("utf-8"), None)
    return "enc:v1:" + base64.b64encode(nonce + ct).decode("ascii")

def decrypt_field(value: str | None) -> str | None:
    if not value or not value.startswith("enc:"):
        return value  # plaintext — backward compat
    # Detects version: "enc:v1:<b64>" or "enc:<b64>" (legacy)
    # Decrypts with the master key corresponding to the version

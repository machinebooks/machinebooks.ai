# Extracted from: LibroAIGateway/cap-32-data-model.md
def get_decrypted_api_key(self) -> str | None:
    """Returns the decrypted API key. Never expose to the client."""
    from app.core.crypto import decrypt_field
    return decrypt_field(self.api_key)

def set_encrypted_api_key(self, plaintext: str | None) -> None:
    """Encrypts and stores the API key."""
    from app.core.crypto import encrypt_field
    self.api_key = encrypt_field(plaintext)

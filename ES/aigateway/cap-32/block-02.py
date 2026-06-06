# Extraído de: LibroAIGateway/cap-32-modelo-de-datos.md
def get_decrypted_api_key(self) -> str | None:
    """Devuelve la API key descifrada. Nunca exponer al cliente."""
    from app.core.crypto import decrypt_field
    return decrypt_field(self.api_key)

def set_encrypted_api_key(self, plaintext: str | None) -> None:
    """Cifra y almacena la API key."""
    from app.core.crypto import encrypt_field
    self.api_key = encrypt_field(plaintext)

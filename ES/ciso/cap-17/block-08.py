# Extraído de: LibroCISO/cap-17-hardening-siem.md
# Generación de clave maestra AES-256 (32 bytes = 256 bits)
import secrets
import base64

key = secrets.token_bytes(32)
key_b64 = base64.b64encode(key).decode()
print(f"ENCRYPTION_KEY={key_b64}")
# Ejemplo de salida: ENCRYPTION_KEY=dGhpcyBpcyBhIDMyLWJ5dGUga2V5IGZvciBBRVM=

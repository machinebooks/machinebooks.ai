# Extraído de: LibroCISO/cap-17-hardening-siem.md
# Ejemplo didáctico: core/encryption.py

import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def get_encryption_key() -> bytes:
    """Obtiene la clave maestra de cifrado desde variable de entorno.

    La clave NUNCA se almacena en código ni en base de datos.
    En producción se inyecta desde un gestor de secretos.
    """
    key_b64 = os.environ.get("ENCRYPTION_KEY")
    if not key_b64:
        raise RuntimeError(
            "ENCRYPTION_KEY no configurada. "
            "Generar con: python -c "
            "'import secrets, base64; "
            "print(base64.b64encode(secrets.token_bytes(32)).decode())'"
        )
    return base64.b64decode(key_b64)


def encrypt_field(plaintext: str) -> str:
    """Cifra un campo de texto con AES-256-GCM.

    Cada llamada genera un IV (nonce) aleatorio de 12 bytes.
    El resultado incluye IV + ciphertext + tag de autenticación,
    codificado en base64 para almacenamiento en VARCHAR/TEXT.

    Formato: base64(iv_12bytes || ciphertext || tag_16bytes)
    """
    key = get_encryption_key()
    aesgcm = AESGCM(key)

    # IV aleatorio: garantiza que cifrar el mismo texto dos veces
    # produce resultados distintos (requisito criptográfico)
    iv = os.urandom(12)

    # Cifrado autenticado: el tag verifica integridad
    ciphertext = aesgcm.encrypt(iv, plaintext.encode("utf-8"), None)

    # Concatenar IV + ciphertext para almacenar como un solo campo
    encrypted_blob = iv + ciphertext
    return base64.b64encode(encrypted_blob).decode("ascii")


def decrypt_field(encrypted_b64: str) -> str:
    """Descifra un campo previamente cifrado con encrypt_field.

    Extrae el IV de los primeros 12 bytes y descifra el resto.
    Si el ciphertext ha sido manipulado, lanza InvalidTag
    (cifrado autenticado = integridad garantizada).
    """
    key = get_encryption_key()
    aesgcm = AESGCM(key)

    encrypted_blob = base64.b64decode(encrypted_b64)

    # Los primeros 12 bytes son el IV
    iv = encrypted_blob[:12]
    ciphertext = encrypted_blob[12:]

    plaintext = aesgcm.decrypt(iv, ciphertext, None)
    return plaintext.decode("utf-8")

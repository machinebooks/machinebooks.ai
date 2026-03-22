# Extraído de: LibroCyberrange/cap-09-fastapi-escala.md
# backend/auth/mfa.py — TOTP con pyotp
import pyotp
from backend.config import settings

def generate_mfa_secret() -> str:
    """Genera un secreto TOTP aleatorio en Base32."""
    return pyotp.random_base32()

def verify_mfa_code(secret: str, code: str) -> bool:
    """Verifica un código TOTP. Permite 1 ventana de deriva (±30 segundos)."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)

def get_provisioning_uri(secret: str, email: str) -> str:
    """URI para generar código QR en la aplicación autenticadora."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=settings.mfa_issuer)

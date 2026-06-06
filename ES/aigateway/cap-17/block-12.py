# Extraído de: LibroAIGateway/cap-17-sso-scim-mfa.md
# gateway/app/services/mfa_service.py — TOTP RFC 6238
class TotpService:
    ISSUER = "N7x Gateway"
    VALID_WINDOW = 1  # ±1 intervalo de 30s (tolerancia a drift)

    @classmethod
    def generate_secret(cls) -> str:
        return pyotp.random_base32()

    @classmethod
    def provisioning_uri(cls, secret: str, email: str) -> str:
        # Genera otpauth://totp/N7x%20IA%20Gateway:user@empresa.com?secret=...
        return pyotp.TOTP(secret).provisioning_uri(
            name=email, issuer_name=cls.ISSUER)

    @classmethod
    def verify(cls, secret: str | None, code: str) -> bool:
        if not secret or not code:
            return False
        try:
            return pyotp.TOTP(secret).verify(
                code.strip(), valid_window=cls.VALID_WINDOW)
        except Exception:
            return False  # fail-closed

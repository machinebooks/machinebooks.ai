# Extraído de: LibroCISO/cap-15-autenticacion-capas.md
import pyotp
import qrcode
import io
import base64

MFA_ISSUER = "GRC Platform"


def generate_mfa_secret() -> str:
    """Genera un secreto TOTP de 32 caracteres (160 bits).
    Se almacena cifrado en la BD, nunca en texto plano."""
    return pyotp.random_base32()


def generate_mfa_qr(secret: str, username: str) -> str:
    """Genera código QR para configurar la app de autenticación.
    El QR codifica una URI otpauth:// con emisor, cuenta y secreto."""
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=username,
        issuer_name=MFA_ISSUER,
    )

    # Generar QR como imagen base64 para enviar al frontend
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def verify_totp(secret: str, code: str) -> bool:
    """Verifica código TOTP con ventana de ±1 intervalo (±30s).
    La ventana compensa desincronización de reloj del dispositivo."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


def user_requires_mfa(user) -> bool:
    """MFA obligatorio para roles privilegiados.
    El ENS categoría Alta lo exige; NIS2 Art. 21 lo presupone."""
    privileged_roles = {"admin", "dpo", "ciso", "security_officer"}
    user_roles = {r.name for r in user.roles}
    return bool(user_roles & privileged_roles) and user.mfa_secret is not None

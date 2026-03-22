# Extraído de: LibroCyberrange/cap-09-fastapi-escala.md
# backend/auth/password_policy.py
import re
from backend.config import settings

def validate_password(password: str) -> tuple[bool, str]:
    """Validar que la contraseña cumple la política de seguridad.
    Returns: (es_valida, mensaje_error)"""
    min_len = settings.password_min_length  # Default: 12

    if len(password) < min_len:
        return False, f"La contraseña debe tener al menos {min_len} caracteres"
    if not re.search(r'[A-Z]', password):
        return False, "Debe contener al menos una mayúscula"
    if not re.search(r'[a-z]', password):
        return False, "Debe contener al menos una minúscula"
    if not re.search(r'\d', password):
        return False, "Debe contener al menos un número"
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'"\\|,.<>/?]', password):
        return False, "Debe contener al menos un carácter especial"

    return True, ""

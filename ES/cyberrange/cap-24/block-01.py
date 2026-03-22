# Extraído de: LibroCyberrange/cap-24-seguridad-plataforma.md
# Política de contraseñas — validación obligatoria en registro y cambio
# Fichero: cyber-range-builder/backend/auth/password_policy.py

def validate_password(password: str) -> tuple[bool, str]:
    """Valida que la contraseña cumple los requisitos de seguridad.
    Retorna (es_valida, mensaje_error)."""
    min_len = settings.password_min_length  # 12 caracteres

    if len(password) < min_len:
        return False, f"La contraseña debe tener al menos {min_len} caracteres"
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una mayúscula"
    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe contener al menos una minúscula"
    if not re.search(r'\d', password):
        return False, "La contraseña debe contener al menos un número"
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'\"\\|,.<>\/?]', password):
        return False, "La contraseña debe contener al menos un carácter especial"
    return True, ""

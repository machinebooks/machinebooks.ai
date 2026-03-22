# Extraído de: LibroCyberrange/cap-08-workzones.md
# Ejemplo didáctico: routers/workzones.py — Verificación de acceso

def check_workzone_access(current_user, workzone_id: int) -> bool:
    """Verificar si el usuario tiene acceso al workzone."""
    # Los administradores acceden a cualquier workzone
    if current_user.role == "admin":
        return True

    # El resto solo accede a su workzone asignado
    if not current_user.workzone_id:
        return False
    return current_user.workzone_id == workzone_id

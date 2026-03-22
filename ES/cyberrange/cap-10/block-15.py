# Extraído de: LibroCyberrange/cap-10-servicios-proxmox.md
# Ejemplo didáctico: normalización de nombres
# Patrón: backend/services/proxmox_sdk_manager.py

@staticmethod
def normalize_vm_name_to_hostname(name: str, max_length: int = 15) -> str:
    """
    Convertir nombre libre en hostname DNS válido.
    "Web Server @2024!" -> "web-server-2024"
    """
    if not name:
        return "vm-unnamed"

    normalized = name.lower().strip()
    # Solo letras, números y guiones
    normalized = re.sub(r'[^a-z0-9\-]', '-', normalized)
    # Reducir guiones multiples
    normalized = re.sub(r'-+', '-', normalized)
    # No empezar ni terminar con guion
    normalized = normalized.strip('-')

    if not normalized:
        return "vm-unnamed"

    # Truncar a longitud maxima (15 chars por compatibilidad)
    if len(normalized) > max_length:
        normalized = normalized[:max_length].rstrip('-')

    # No empezar con número
    if normalized[0].isdigit():
        normalized = "vm-" + normalized
        if len(normalized) > max_length:
            normalized = normalized[:max_length].rstrip('-')

    return normalized

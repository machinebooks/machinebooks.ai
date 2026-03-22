# Extraído de: LibroBugBounty/cap-05-asar-tampering.md
# Ejemplo de recÃ¡lculo de offsets
# Estructura original:
# main.js: offset=0, size=2847
# preload.js: offset=2847, size=1203
# utils.js: offset=4050, size=890

# DespuÃ©s de inyectar 200 bytes en main.js:
# main.js: offset=0, size=3047 (+200)
# preload.js: offset=3047, size=1203 (offset+200)
# utils.js: offset=4250, size=890 (offset+200)

def recalculate_offsets(header: dict, modified_file: str,
                        size_diff: int) -> dict:
    """Recalcula offsets de todos los ficheros despuÃ©s del modificado."""
    modified_offset = None

    def find_offset(node, target_path, current_path=""):
        nonlocal modified_offset
        if "files" in node:
            for name, child in node["files"].items():
                child_path = f"{current_path}/{name}" if current_path else name
                find_offset(child, target_path, child_path)
        elif "offset" in node:
            if current_path == target_path:
                modified_offset = int(node["offset"])

    find_offset(header, modified_file)

    if modified_offset is None:
        raise ValueError(f"Fichero no encontrado: {modified_file}")

    def update(node):
        if "files" in node:
            for child in node["files"].values():
                update(child)
        elif "offset" in node:
            if int(node["offset"]) > modified_offset:
                node["offset"] = str(int(node["offset"]) + size_diff)

    update(header)
    return header

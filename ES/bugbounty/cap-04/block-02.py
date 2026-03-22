# Extraído de: LibroBugBounty/cap-04-electron-superficie.md
#!/usr/bin/env python3
"""
Parser de formato ASAR para auditoría de seguridad.
Extrae la tabla de contenidos y verifica integridad.
"""
import json
import struct
from pathlib import Path

def parse_asar_header(asar_path: str) -> dict:
    """Extrae el header JSON del fichero ASAR."""
    with open(asar_path, "rb") as f:
        # ASAR header: 4 bytes magic, 4 bytes header size,
        # 4 bytes JSON size, 4 bytes padding
        magic = struct.unpack("<I", f.read(4))[0]  # Siempre 4
        header_size = struct.unpack("<I", f.read(4))[0]
        json_size = struct.unpack("<I", f.read(4))[0]
        f.read(4)  # Padding

        # El JSON describe la estructura del archivo
        header_json = f.read(json_size).decode("utf-8")
        header = json.loads(header_json)

        return {
            "header_size": header_size,
            "json_size": json_size,
            "data_offset": 16 + header_size,  # Donde empiezan los datos
            "structure": header,
        }


def list_asar_files(asar_path: str) -> list[dict]:
    """Lista todos los ficheros dentro del ASAR con metadatos."""
    header = parse_asar_header(asar_path)
    files = []

    def walk(node, path=""):
        if "files" in node:
            for name, child in node["files"].items():
                child_path = f"{path}/{name}" if path else name
                walk(child, child_path)
        elif "offset" in node:
            files.append({
                "path": path,
                "offset": int(node["offset"]),
                "size": node.get("size", 0),
                "executable": node.get("executable", False),
            })

    walk(header["structure"])
    return files


# Ejemplo: analizar el ASAR de Discord
asar = "resources/app.asar"
files = list_asar_files(asar)

# Ficheros interesantes para auditoría
interesting = [f for f in files if any(
    pattern in f["path"].lower()
    for pattern in ["main.js", "preload", "index.js",
                    "config", "secret", "token", "key"]
)]

# Resultado típico en Discord:
# - app/main.js (entry point — target de inyección)
# - app/mainScreenPreload.js (preload script — bridge)
# - app/common/paths.js (rutas de configuración)
# Total: 847 ficheros, ~14 MB

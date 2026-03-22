# Extraído de: LibroBugBounty/cap-04-electron-superficie.md
#!/usr/bin/env python3
"""
Extractor de ficheros ASAR para auditoría de código JavaScript.
Extrae ficheros específicos sin desempaquetar todo el archivo.
"""
import json
import struct
from pathlib import Path

def extract_file_from_asar(asar_path: str, target_file: str) -> bytes:
    """Extrae un fichero específico del ASAR."""
    with open(asar_path, "rb") as f:
        # Leer header
        f.read(4)  # magic
        header_size = struct.unpack("<I", f.read(4))[0]
        json_size = struct.unpack("<I", f.read(4))[0]
        f.read(4)  # padding

        header = json.loads(f.read(json_size).decode("utf-8"))
        data_offset = 16 + header_size

        # Buscar fichero en el header
        parts = target_file.split("/")
        node = header
        for part in parts:
            if "files" in node and part in node["files"]:
                node = node["files"][part]
            else:
                raise FileNotFoundError(f"No encontrado: {target_file}")

        # Leer datos del fichero
        file_offset = data_offset + int(node["offset"])
        file_size = node["size"]
        f.seek(file_offset)
        return f.read(file_size)


# Extraer main.js de Discord para análisis
main_js = extract_file_from_asar(
    "resources/app.asar", "app/main.js"
)
content = main_js.decode("utf-8")

# Claude analiza el contenido buscando:
# 1. Verificaciones de integridad (¿comprueba hash del ASAR?)
# 2. Uso de contextIsolation y nodeIntegration
# 3. Preload scripts y su configuración
# 4. Rutas hardcodeadas y secretos
# 5. Mecanismos de actualización (Squirrel)

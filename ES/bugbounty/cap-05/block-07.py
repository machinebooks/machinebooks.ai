# Extraído de: LibroBugBounty/cap-05-asar-tampering.md
#!/usr/bin/env python3
"""
Detector forense de ASAR tampering.
Compara un ASAR posiblemente comprometido con una referencia limpia.
"""
import hashlib
import json
import struct
from pathlib import Path
from datetime import datetime

def forensic_asar_check(suspect_asar: str,
                         reference_hash: str = None) -> dict:
    """AnÃ¡lisis forense de un fichero ASAR."""
    path = Path(suspect_asar)
    data = path.read_bytes()

    result = {
        "file": str(path),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "modified": datetime.fromtimestamp(
            path.stat().st_mtime
        ).isoformat(),
        "indicators": [],
    }

    # Verificar hash contra referencia
    if reference_hash and result["sha256"] != reference_hash:
        result["indicators"].append({
            "severity": "CRITICAL",
            "finding": "Hash no coincide con referencia limpia",
            "expected": reference_hash[:16] + "...",
            "actual": result["sha256"][:16] + "...",
        })

    # Extraer header para anÃ¡lisis
    with open(suspect_asar, "rb") as f:
        f.read(4)  # pickle size
        header_size = struct.unpack("<I", f.read(4))[0]
        json_size = struct.unpack("<I", f.read(4))[0]
        f.read(4)
        header_json = f.read(json_size).decode("utf-8")

    header = json.loads(header_json)

    # Buscar ficheros sospechosos en el ASAR
    def walk_files(node, path=""):
        findings = []
        if "files" in node:
            for name, child in node["files"].items():
                child_path = f"{path}/{name}" if path else name
                findings.extend(walk_files(child, child_path))
        elif "offset" in node:
            # Ficheros sospechosos por nombre
            lower = path.lower()
            if any(s in lower for s in [
                "payload", "inject", "hack", "exploit",
                "poc", "backdoor", "shell",
            ]):
                findings.append({
                    "severity": "HIGH",
                    "finding": f"Nombre sospechoso: {path}",
                })
        return findings

    result["indicators"].extend(walk_files(header))

    # Verificar si main.js tiene contenido aÃ±adido al inicio
    # (patrÃ³n tÃ­pico de tampering: payload antes del cÃ³digo legÃ­timo)
    try:
        main_node = header["files"]["app"]["files"]["main.js"]
        main_offset = 16 + header_size + int(main_node["offset"])
        main_data = data[main_offset:main_offset + min(500, main_node["size"])]
        main_text = main_data.decode("utf-8", errors="ignore")

        # El cÃ³digo legÃ­timo de Electron suele empezar con
        # 'use strict' o require(). Un payload suele empezar
        # con require('child_process') o con comentarios de PoC
        suspicious_starts = [
            "require('child_process')",
            "require(\"child_process\")",
            "execSync", "exec(",
            "// PoC", "// payload", "// inject",
            "const {execSync}", "const { execSync }",
        ]
        for pattern in suspicious_starts:
            if pattern in main_text[:200]:
                result["indicators"].append({
                    "severity": "CRITICAL",
                    "finding": f"main.js comienza con patrÃ³n "
                               f"sospechoso: '{pattern}'",
                })
                break

    except (KeyError, IndexError):
        pass

    result["tampered"] = any(
        i["severity"] == "CRITICAL" for i in result["indicators"]
    )
    return result

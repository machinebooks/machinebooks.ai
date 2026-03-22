# Extraído de: LibroBugBounty/cap-01-primera-vuln-agente.md
#!/usr/bin/env python3
"""
Enumeración automatizada de Electron Fuses.
Busca el sentinel 'dL7pKGdnNz796PbbjQWNKmHXBZaB9tsX'
y extrae el estado de cada fuse.
"""
import struct
from pathlib import Path

# Sentinel que marca el inicio de la tabla de fuses
SENTINEL = b"dL7pKGdnNz796PbbjQWNKmHXBZaB9tsX"

# Fuses conocidos (Electron 28+)
FUSE_DEFS = {
    1: ("RunAsNode",
        "CRITICAL - Permite ejecutar como Node.js puro"),
    2: ("EnableCookieEncryption",
        "Cifrado de cookies en disco"),
    3: ("EnableNodeOptionsEnvironmentVariable",
        "CRITICAL - NODE_OPTIONS puede inyectar código"),
    4: ("EnableNodeCliInspectArguments",
        "Permite --inspect para debug remoto"),
    5: ("EnableEmbeddedAsarIntegrityValidation",
        "Verifica integridad del ASAR"),
    6: ("OnlyLoadAppFromAsar",
        "CRITICAL - Si deshabilitado, carga app/ además de app.asar"),
    7: ("LoadBrowserProcessSpecificV8Snapshot",
        "Snapshot V8 específico del proceso browser"),
    8: ("GrantFileProtocolExtraPrivileges",
        "Privilegios extra para file://"),
}

def analyze_fuses(exe_path: str) -> dict:
    """Extrae y analiza los fuses de un ejecutable Electron."""
    data = Path(exe_path).read_bytes()
    offset = data.find(SENTINEL)

    if offset == -1:
        return {"error": "No Electron o fuses no encontrados"}

    fuse_start = offset + len(SENTINEL)
    fuses = {}
    critical_issues = []

    for fuse_id, (name, description) in FUSE_DEFS.items():
        if fuse_start + fuse_id - 1 < len(data):
            value = data[fuse_start + fuse_id - 1]
            enabled = value == 1
            fuses[name] = {
                "enabled": enabled,
                "description": description,
            }
            # Configuraciones peligrosas
            if name == "RunAsNode" and enabled:
                critical_issues.append(
                    "RunAsNode habilitado: ELECTRON_RUN_AS_NODE "
                    "permite ejecución Node.js arbitraria"
                )
            if name == "EnableCookieEncryption" and not enabled:
                critical_issues.append(
                    "Cifrado de cookies deshabilitado: "
                    "tokens de sesión accesibles en disco"
                )
            if name == "OnlyLoadAppFromAsar" and not enabled:
                critical_issues.append(
                    "OnlyLoadAppFromAsar deshabilitado: "
                    "permite cargar código desde directorio app/"
                )

    return {
        "fuses": fuses,
        "critical_issues": critical_issues,
        "sentinel_offset": hex(offset),
    }

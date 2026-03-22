# Extraído de: LibroBugBounty/cap-01-primera-vuln-agente.md
#!/usr/bin/env python3
"""
Reconocimiento automatizado de superficie de ataque
en aplicaciones de escritorio Windows.
Claude Code genera y ejecuta este script como primer paso.
"""
import os
import pefile
import subprocess
from pathlib import Path
from collections import defaultdict

def recon_directory(app_path: str) -> dict:
    """Analiza un directorio de aplicación y genera triaje."""
    results = {
        "executables": [],
        "dlls": [],
        "unsigned": [],
        "writable_dirs": [],
        "electron_indicators": [],
    }

    app = Path(app_path)
    all_files = list(app.rglob("*"))

    for f in all_files:
        if not f.is_file():
            continue

        # Detectar indicadores Electron
        if f.name in ("electron.exe", "resources.pak", "app.asar"):
            results["electron_indicators"].append(str(f))

        # Clasificar ejecutables y DLLs
        if f.suffix.lower() == ".exe":
            results["executables"].append(analyze_pe(f))
        elif f.suffix.lower() == ".dll":
            results["dlls"].append(analyze_pe(f))

    # Verificar permisos de directorio (icacls en Windows)
    for d in app.rglob("*"):
        if d.is_dir():
            try:
                acl = subprocess.check_output(
                    ["icacls", str(d)],
                    stderr=subprocess.DEVNULL, text=True
                )
                # Full control para usuarios sin privilegios
                if "BUILTIN\\Users:(OI)(CI)(F)" in acl:
                    results["writable_dirs"].append(str(d))
            except subprocess.CalledProcessError:
                pass

    return results


def analyze_pe(filepath: Path) -> dict:
    """Extrae metadatos de seguridad de un PE."""
    try:
        pe = pefile.PE(str(filepath), fast_load=True)
        pe.parse_data_directories()

        has_signature = hasattr(pe, "DIRECTORY_ENTRY_SECURITY")
        dll_chars = pe.OPTIONAL_HEADER.DllCharacteristics
        security = {
            "aslr": bool(dll_chars & 0x0040),
            "dep": bool(dll_chars & 0x0100),
            "cfg": bool(dll_chars & 0x4000),
        }

        return {
            "path": str(filepath),
            "name": filepath.name,
            "signed": has_signature,
            "security": security,
            "size": filepath.stat().st_size,
        }
    except Exception as e:
        return {"path": str(filepath), "error": str(e)}

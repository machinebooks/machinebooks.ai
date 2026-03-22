# Extraído de: LibroBugBounty/cap-06-dll-sideloading.md
#!/usr/bin/env python3
"""
Detector de DLL sideloading en tiempo real.
Monitoriza un directorio de aplicaciÃ³n y alerta si aparecen
DLLs que coinciden con nombres de DLLs del sistema.
"""
import os
import hashlib
import json
from pathlib import Path
from datetime import datetime

# DLLs del sistema que son candidatas frecuentes de hijacking
KNOWN_SYSTEM_DLLS = {
    "VERSION.dll", "USERENV.dll", "DBGHELP.dll",
    "WINMM.dll", "WINSPOOL.DRV", "DWMAPI.dll",
    "PROPSYS.dll", "UXTHEME.dll", "PROFAPI.dll",
    "CRYPTBASE.dll", "MSASN1.dll", "ncrypt.dll",
}

def audit_for_sideloading(app_dir: str) -> list[dict]:
    """Detecta posibles DLLs sideloaded en un directorio."""
    findings = []
    sys32 = Path(os.environ["SYSTEMROOT"]) / "System32"

    for dll_name in KNOWN_SYSTEM_DLLS:
        local_dll = Path(app_dir) / dll_name
        system_dll = sys32 / dll_name

        if local_dll.exists() and system_dll.exists():
            # Hay una copia local de una DLL del sistema
            local_hash = hashlib.sha256(
                local_dll.read_bytes()
            ).hexdigest()
            system_hash = hashlib.sha256(
                system_dll.read_bytes()
            ).hexdigest()

            if local_hash != system_hash:
                findings.append({
                    "dll": dll_name,
                    "severity": "CRITICAL",
                    "reason": "DLL local difiere de System32",
                    "local_hash": local_hash[:16] + "...",
                    "system_hash": system_hash[:16] + "...",
                    "local_size": local_dll.stat().st_size,
                    "system_size": system_dll.stat().st_size,
                    "detected_at": datetime.now().isoformat(),
                })

    return findings

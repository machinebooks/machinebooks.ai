# Extraído de: LibroBugBounty/cap-04-electron-superficie.md
#!/usr/bin/env python3
"""
Auditoría de seguridad de aplicaciones Electron.
Analiza fuses, permisos de directorio, firma digital
y configuración de ASAR en una pasada.
"""
import os
import json
import subprocess
from pathlib import Path
from dataclasses import dataclass, asdict

SENTINEL = b"dL7pKGdnNz796PbbjQWNKmHXBZaB9tsX"

@dataclass
class FuseResult:
    name: str
    enabled: bool
    security_impact: str
    recommendation: str

FUSE_MAP = {
    1: ("RunAsNode",
        "Permite ejecución como Node.js puro via ELECTRON_RUN_AS_NODE",
        "Deshabilitar en producción"),
    2: ("EnableCookieEncryption",
        "Cifra cookies y tokens en disco",
        "Habilitar siempre"),
    3: ("EnableNodeOptionsEnvironmentVariable",
        "Permite NODE_OPTIONS para inyección de módulos",
        "Deshabilitar en producción"),
    4: ("EnableNodeCliInspectArguments",
        "Permite --inspect para debug remoto",
        "Deshabilitar en producción"),
    5: ("EnableEmbeddedAsarIntegrityValidation",
        "Verifica integridad del ASAR al cargar",
        "Habilitar siempre"),
    6: ("OnlyLoadAppFromAsar",
        "Solo carga código desde app.asar, no desde app/",
        "Habilitar siempre"),
    7: ("LoadBrowserProcessSpecificV8Snapshot",
        "Snapshot V8 para el proceso browser",
        "Habilitar para defensa en profundidad"),
    8: ("GrantFileProtocolExtraPrivileges",
        "Privilegios extra para protocolo file://",
        "Deshabilitar si no es necesario"),
}

def extract_fuses(exe_path: Path) -> list[FuseResult]:
    """Extrae fuses de un ejecutable Electron."""
    data = exe_path.read_bytes()
    offset = data.find(SENTINEL)
    if offset == -1:
        return []

    fuse_start = offset + len(SENTINEL)
    results = []

    for fuse_id, (name, impact, recommendation) in FUSE_MAP.items():
        idx = fuse_start + fuse_id - 1
        if idx < len(data):
            enabled = data[idx] == 1
            results.append(FuseResult(
                name=name,
                enabled=enabled,
                security_impact=impact,
                recommendation=recommendation,
            ))
    return results


def check_directory_permissions(app_dir: Path) -> dict:
    """Verifica si el directorio es escribible sin admin."""
    try:
        result = subprocess.run(
            ["icacls", str(app_dir)],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout
        writable = any(perm in output for perm in [
            "BUILTIN\\Users:(OI)(CI)(F)",
            "BUILTIN\\Users:(OI)(CI)(M)",
            "Everyone:(OI)(CI)(F)",
        ])
        return {
            "writable_by_user": writable,
            "install_location": str(app_dir),
            "in_program_files": "Program Files" in str(app_dir),
        }
    except Exception as e:
        return {"error": str(e)}


def check_asar(app_dir: Path) -> dict:
    """Verifica configuración del ASAR."""
    asar_path = app_dir / "resources" / "app.asar"
    app_dir_path = app_dir / "resources" / "app"

    return {
        "asar_exists": asar_path.exists(),
        "asar_size": asar_path.stat().st_size if asar_path.exists() else 0,
        "app_dir_exists": app_dir_path.exists(),
        "app_dir_coexists": asar_path.exists() and app_dir_path.exists(),
    }


def full_audit(exe_path: str) -> dict:
    """Auditoría completa de seguridad Electron."""
    exe = Path(exe_path)
    app_dir = exe.parent

    fuses = extract_fuses(exe)
    permissions = check_directory_permissions(app_dir)
    asar = check_asar(app_dir)

    # Evaluación de riesgo
    critical = []
    if any(f.name == "RunAsNode" and f.enabled for f in fuses):
        critical.append("RunAsNode habilitado")
    if any(f.name == "EnableCookieEncryption" and not f.enabled for f in fuses):
        critical.append("Cifrado de cookies deshabilitado")
    if any(f.name == "OnlyLoadAppFromAsar" and not f.enabled for f in fuses):
        critical.append("ASAR integrity no forzada")
    if permissions.get("writable_by_user"):
        critical.append("Directorio escribible sin admin")

    return {
        "application": exe.name,
        "fuses": [asdict(f) for f in fuses],
        "permissions": permissions,
        "asar": asar,
        "critical_issues": critical,
        "risk_level": "CRITICAL" if len(critical) >= 3
                      else "HIGH" if len(critical) >= 2
                      else "MEDIUM" if len(critical) >= 1
                      else "LOW",
    }

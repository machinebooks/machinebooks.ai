# Extraído de: LibroBugBounty/cap-16-reconocimiento-surface.md
import subprocess
import json
from pathlib import Path

def audit_filesystem_permissions(install_dir):
    """Audita permisos de todos los ficheros en el directorio."""
    findings = []

    for item in Path(install_dir).rglob("*"):
        try:
            # Ejecutar icacls para obtener DACL
            result = subprocess.run(
                ["icacls", str(item)],
                capture_output=True, text=True, timeout=5
            )

            acl_text = result.stdout
            risk = "LOW"
            issues = []

            # Buscar permisos peligrosos para usuarios no-admin
            if "BUILTIN\\Users:(F)" in acl_text:
                risk = "HIGH"
                issues.append("Users have FULL CONTROL")
            elif "BUILTIN\\Users:(M)" in acl_text:
                risk = "HIGH"
                issues.append("Users have MODIFY")
            elif "BUILTIN\\Users:(W)" in acl_text:
                risk = "MEDIUM"
                issues.append("Users have WRITE")

            # Herencia que propaga permisos
            if "(OI)(CI)" in acl_text and risk != "LOW":
                issues.append("Inherits to all children")

            # Clasificar tipo de fichero
            suffix = item.suffix.lower()
            if suffix in ('.exe', '.dll', '.sys'):
                file_type = "BINARY"
                if risk == "HIGH":
                    risk = "CRITICAL"  # Binario writable = RCE potencial
            elif suffix in ('.config', '.json', '.xml', '.vdf'):
                file_type = "CONFIG"
            else:
                file_type = "OTHER"

            if issues:
                findings.append({
                    "path": str(item),
                    "type": file_type,
                    "risk": risk,
                    "issues": issues,
                    "is_dir": item.is_dir(),
                    "suffix": suffix,
                })

        except (subprocess.TimeoutExpired, PermissionError):
            pass

    return findings

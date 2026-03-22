# Extraído de: LibroBugBounty/cap-04-electron-superficie.md
#!/usr/bin/env python3
"""
Verificación de firma digital de DLLs en directorio de aplicación.
Identifica DLLs sin firma que pueden ser reemplazadas por proxy DLLs.
"""
import subprocess
from pathlib import Path

def check_signature(dll_path: Path) -> dict:
    """Verifica si una DLL tiene firma digital válida."""
    try:
        # signtool verify con output detallado
        result = subprocess.run(
            ["powershell", "-Command",
             f"Get-AuthenticodeSignature '{dll_path}' | "
             f"Select-Object Status, SignerCertificate"],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout
        signed = "Valid" in output
        signer = ""
        if "SignerCertificate" in output:
            # Extraer nombre del firmante
            for line in output.split('\n'):
                if "CN=" in line:
                    signer = line.strip()
                    break

        return {
            "path": str(dll_path),
            "name": dll_path.name,
            "signed": signed,
            "signer": signer,
            "size": dll_path.stat().st_size,
        }
    except Exception as e:
        return {
            "path": str(dll_path),
            "name": dll_path.name,
            "error": str(e),
        }


def audit_dll_signatures(app_dir: str) -> dict:
    """Audita todas las DLLs en un directorio de aplicación."""
    dlls = list(Path(app_dir).rglob("*.dll"))
    results = {"total": len(dlls), "unsigned": [], "signed": []}

    for dll in dlls:
        sig = check_signature(dll)
        if sig.get("signed"):
            results["signed"].append(sig)
        else:
            results["unsigned"].append(sig)

    results["unsigned_count"] = len(results["unsigned"])
    results["unsigned_ratio"] = (
        len(results["unsigned"]) / len(dlls) * 100
        if dlls else 0
    )

    return results

# Resultado en Discord: 12 DLLs sin firma de 214 totales (5.6%)
# Cada DLL sin firma es un candidato para proxy DLL hijacking

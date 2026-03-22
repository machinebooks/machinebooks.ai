# Extraído de: LibroBugBounty/cap-06-dll-sideloading.md
#!/usr/bin/env python3
"""
AnÃ¡lisis de tablas de importaciÃ³n para DLL sideloading.
Clasifica cada DLL importada por riesgo de hijacking.
"""
import pefile
import os
from pathlib import Path

def analyze_imports_for_hijacking(exe_path: str) -> dict:
    """Analiza un PE y clasifica sus imports por riesgo de hijacking."""
    pe = pefile.PE(exe_path)
    exe_dir = Path(exe_path).parent

    results = {
        "executable": Path(exe_path).name,
        "total_imports": 0,
        "hijackable": [],
        "phantom": [],
        "protected": [],
    }

    if not hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
        return results

    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        dll_name = entry.dll.decode()
        results["total_imports"] += 1

        # Contar exports que necesitarÃ­amos forwardear
        export_count = len(entry.imports)

        # Â¿Existe en el directorio de la aplicaciÃ³n?
        local_exists = (exe_dir / dll_name).exists()

        # Â¿Existe en System32?
        sys32 = Path(os.environ["SYSTEMROOT"]) / "System32" / dll_name
        sys32_exists = sys32.exists()

        # Clasificar
        if not sys32_exists and not local_exists:
            # Phantom DLL: no existe en ningÃºn sitio
            results["phantom"].append({
                "dll": dll_name,
                "exports_needed": export_count,
                "risk": "CRITICAL â€” phantom DLL, fÃ¡cil de suplantar",
            })
        elif not local_exists and sys32_exists:
            # Candidata a sideloading: existe en System32
            # pero no en el directorio local
            results["hijackable"].append({
                "dll": dll_name,
                "exports_needed": export_count,
                "system_path": str(sys32),
                "risk": "HIGH â€” candidata a proxy DLL",
            })
        else:
            results["protected"].append({
                "dll": dll_name,
                "local_path": str(exe_dir / dll_name) if local_exists else None,
            })

    return results

# Ejemplo: anÃ¡lisis de Steam.exe
# result = analyze_imports_for_hijacking(
#     r"C:\Program Files (x86)\Steam\Steam.exe"
# )
#
# Resultado relevante:
# hijackable: [
#   {"dll": "VERSION.dll", "exports_needed": 6, "risk": "HIGH"},
#   {"dll": "USERENV.dll", "exports_needed": 3, "risk": "HIGH"},
#   {"dll": "DBGHELP.dll", "exports_needed": 217, "risk": "HIGH"},
# ]
# phantom: [
#   {"dll": "TextShaping.dll", "exports_needed": 1, "risk": "CRITICAL"},
# ]

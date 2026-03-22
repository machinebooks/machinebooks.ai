# Extraído de: LibroBugBounty/cap-06-dll-sideloading.md
#!/usr/bin/env python3
"""
Detector de Phantom DLLs.
Identifica DLLs importadas que no existen en ninguna
ubicaciÃ³n del sistema â€” candidatas perfectas para hijacking.
"""
import pefile
import os
from pathlib import Path

def find_phantom_dlls(exe_path: str) -> list[dict]:
    """Encuentra DLLs importadas que no existen en el sistema."""
    pe = pefile.PE(exe_path)
    exe_dir = Path(exe_path).parent
    sys32 = Path(os.environ["SYSTEMROOT"]) / "System32"
    syswow = Path(os.environ["SYSTEMROOT"]) / "SysWOW64"
    path_dirs = os.environ.get("PATH", "").split(";")

    phantoms = []

    if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
        for entry in pe.DIRECTORY_ENTRY_IMPORT:
            dll_name = entry.dll.decode()

            # Buscar en todas las ubicaciones posibles
            found = False
            search_paths = [exe_dir, sys32, syswow] + [
                Path(p) for p in path_dirs if p
            ]
            for search_dir in search_paths:
                if (search_dir / dll_name).exists():
                    found = True
                    break

            if not found:
                phantoms.append({
                    "dll": dll_name,
                    "imports_count": len(entry.imports),
                    "risk": "CRITICAL â€” no existe en el sistema",
                    "exploit_complexity": "TRIVIAL â€” no requiere proxy",
                })

    return phantoms

# Resultado en Steam: TextShaping.dll no existe
# â†’ DLL de 0 exports necesarios, payload puro

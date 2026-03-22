# Extraído de: LibroBugBounty/cap-06-dll-sideloading.md
#!/usr/bin/env python3
"""
Triaje automatizado de DLL hijacking para mÃºltiples aplicaciones.
Claude genera este script y lo ejecuta contra cada target.
"""
import pefile
import json
from pathlib import Path

# Directorio donde estÃ¡n los ejecutables de cada app
TARGETS = {
    "Discord": r"C:\Users\researcher\AppData\Local\Discord\app-1.0.9045\Discord.exe",
    "Steam": r"C:\Program Files (x86)\Steam\Steam.exe",
    "Wand": r"C:\Users\researcher\AppData\Local\Programs\wand\Wand.exe",
}

def triage_dll_hijacking(targets: dict) -> dict:
    """Triaje comparativo de DLL hijacking entre aplicaciones."""
    results = {}

    for name, exe_path in targets.items():
        if not Path(exe_path).exists():
            results[name] = {"error": "No encontrado"}
            continue

        pe = pefile.PE(exe_path)
        exe_dir = Path(exe_path).parent

        # Â¿El directorio es escribible sin admin?
        writable = not str(exe_dir).startswith("C:\\Program Files")

        candidates = []
        if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                dll_name = entry.dll.decode()
                local = (exe_dir / dll_name).exists()
                # Si la DLL no estÃ¡ en el directorio local,
                # es candidata a sideloading
                if not local:
                    candidates.append({
                        "dll": dll_name,
                        "exports": len(entry.imports),
                    })

        results[name] = {
            "writable_dir": writable,
            "total_imports": len(pe.DIRECTORY_ENTRY_IMPORT)
                            if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT') else 0,
            "hijack_candidates": len(candidates),
            "top_candidates": sorted(
                candidates, key=lambda x: x["exports"]
            )[:5],  # Las 5 DLLs con menos exports (mÃ¡s fÃ¡ciles)
            "risk": "CRITICAL" if writable and candidates
                    else "HIGH" if candidates
                    else "LOW",
        }

    return results

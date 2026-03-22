# Extraído de: LibroBugBounty/cap-02-stack-hunter.md
#!/usr/bin/env python3
"""
AnÃ¡lisis de PE/driver: imports peligrosos, secciones, seguridad.
Generado por Claude Code, ejecutado en el contenedor Docker.
"""
import pefile
import lief
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()
DRIVER_DIR = Path("/lab/drivers")
RESULTS_DIR = Path("/lab/results")

# Importaciones que indican primitivas de kernel r/w
DANGEROUS_IMPORTS = {
    "MmMapIoSpace":
        "Mapea memoria fÃ­sica â€” r/w arbitraria",
    "ZwMapViewOfSection":
        "Mapea secciÃ³n en proceso â€” mapeo potencial",
    "MmCopyMemory":
        "Copia memoria fÃ­sica/virtual â€” lectura",
    "MmMapLockedPages":
        "Mapea pÃ¡ginas bloqueadas â€” mapeo arbitrario",
    "ZwOpenProcess":
        "Abre handle de proceso â€” escalada de privilegios",
    "KeStackAttachProcess":
        "Attach a proceso â€” acceso cross-process",
}

def analyze_driver(filepath):
    """AnÃ¡lisis completo de un driver."""
    pe = pefile.PE(str(filepath))
    report = {"file": filepath.name, "dangerous": []}

    # Verificar features de seguridad
    dll_chars = pe.OPTIONAL_HEADER.DllCharacteristics
    report["security"] = {
        "ASLR": bool(dll_chars & 0x0040),
        "DEP": bool(dll_chars & 0x0100),
        "CFG": bool(dll_chars & 0x4000),
    }

    # Buscar importaciones peligrosas
    if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
        for entry in pe.DIRECTORY_ENTRY_IMPORT:
            for imp in entry.imports:
                if imp.name:
                    name = imp.name.decode()
                    if name in DANGEROUS_IMPORTS:
                        report["dangerous"].append({
                            "function": name,
                            "risk": DANGEROUS_IMPORTS[name],
                        })

    # Risk score: 0-15
    score = len(report["dangerous"]) * 2
    if not report["security"]["CFG"]:
        score += 2
    report["risk_score"] = min(score, 15)

    return report

# Analizar todos los drivers y guardar resultado
reports = []
for driver in sorted(DRIVER_DIR.glob("*.sys")):
    reports.append(analyze_driver(driver))

output = RESULTS_DIR / "pe_analysis.json"
with open(output, "w") as f:
    json.dump(reports, f, indent=2)
console.print(f"[green]AnÃ¡lisis guardado en {output}[/green]")

# Extraído de: LibroBugBounty/cap-16-reconocimiento-surface.md
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from datetime import datetime

class DesktopAppScanner:
    """Escáner automatizado de aplicaciones de escritorio."""

    # Ubicaciones comunes de aplicaciones
    COMMON_PATHS = [
        Path("C:/Program Files"),
        Path("C:/Program Files (x86)"),
        Path.home() / "AppData" / "Local",
        Path.home() / "AppData" / "Roaming",
    ]

    def __init__(self, targets):
        """targets: lista de nombres de aplicación a escanear."""
        self.targets = targets
        self.results = {}

    def discover_installations(self):
        """Descubre paths de instalación para cada target."""
        installations = {}
        for target in self.targets:
            for base in self.COMMON_PATHS:
                candidates = list(base.glob(f"*{target}*"))
                for c in candidates:
                    if c.is_dir():
                        installations.setdefault(target, []).append(c)
        return installations

    def scan_target(self, name, install_dir):
        """Ejecuta auditoría completa de un target."""
        result = {
            "target": name,
            "path": str(install_dir),
            "timestamp": datetime.now().isoformat(),
        }

        # Fase 1: Contar ficheros y clasificar
        all_files = list(install_dir.rglob("*"))
        result["total_files"] = len(all_files)

        exes = [f for f in all_files if f.suffix.lower() == '.exe']
        dlls = [f for f in all_files if f.suffix.lower() == '.dll']
        result["exes"] = len(exes)
        result["dlls"] = len(dlls)

        # Fase 2: Verificar permisos del directorio raíz
        icacls = subprocess.run(
            ["icacls", str(install_dir)],
            capture_output=True, text=True, timeout=10
        )
        result["root_acl"] = icacls.stdout.strip()
        result["users_writable"] = "Users:(F)" in icacls.stdout

        # Fase 3: Buscar servicios relacionados
        sc = subprocess.run(
            ["sc", "query", "type=", "service", "state=", "all"],
            capture_output=True, text=True
        )
        # Filtrar servicios por nombre del target
        services = [
            line.split()[-1]
            for line in sc.stdout.split('\n')
            if "SERVICE_NAME" in line
            and name.lower() in line.lower()
        ]
        result["services"] = services

        return result

    def run_full_scan(self):
        """Ejecuta escaneo completo de todos los targets."""
        installations = self.discover_installations()

        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {}
            for name, paths in installations.items():
                for path in paths:
                    future = pool.submit(self.scan_target, name, path)
                    futures[future] = (name, path)

            for future in futures:
                name, path = futures[future]
                self.results[f"{name}:{path}"] = future.result()

        return self.results

# Uso
scanner = DesktopAppScanner(["Epic", "Steam", "Discord", "Wand"])
results = scanner.run_full_scan()

# Guardar para análisis con Claude
with open("multi_target_audit.json", "w") as f:
    json.dump(results, f, indent=2)

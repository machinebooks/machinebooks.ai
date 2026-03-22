# Extraído de: LibroBugBounty/cap-16-reconocimiento-surface.md
import subprocess
from pathlib import Path
from collections import Counter

def analyze_inheritance(install_dir):
    """Analiza la cadena de herencia de permisos."""
    inheritance_stats = Counter()
    critical_inherited = []

    for item in Path(install_dir).rglob("*"):
        try:
            result = subprocess.run(
                ["icacls", str(item)],
                capture_output=True, text=True, timeout=5
            )
            acl = result.stdout

            # Detectar permisos heredados vs explícitos
            if "(I)(F)" in acl and "BUILTIN\\Users" in acl:
                inheritance_stats["inherited_fullcontrol"] += 1
                # Marcar binarios heredados como críticos
                if item.suffix.lower() in ('.exe', '.dll', '.sys'):
                    critical_inherited.append({
                        "path": str(item),
                        "inherited": True,
                        "suffix": item.suffix.lower(),
                    })
            elif "(F)" in acl and "(I)" not in acl:
                inheritance_stats["explicit_fullcontrol"] += 1

        except (subprocess.TimeoutExpired, PermissionError):
            pass

    return {
        "total_inherited_fc": inheritance_stats["inherited_fullcontrol"],
        "total_explicit_fc": inheritance_stats["explicit_fullcontrol"],
        "critical_binaries": critical_inherited,
    }

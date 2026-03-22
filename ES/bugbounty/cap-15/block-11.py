# Extraído de: LibroBugBounty/cap-15-token-theft-persistencia.md
import winreg
from pathlib import Path

def check_squirrel_persistence():
    """Verifica puntos de persistencia de Squirrel en el registro."""
    findings = []

    # Squirrel registra entries en Run/RunOnce
    run_keys = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
    ]

    for hive, subkey in run_keys:
        try:
            key = winreg.OpenKey(hive, subkey)
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    if "update.exe" in value.lower() or "squirrel" in value.lower():
                        findings.append({
                            "key": subkey,
                            "name": name,
                            "value": value,
                            "type": "SQUIRREL_UPDATER",
                        })
                    i += 1
                except WindowsError:
                    break
            winreg.CloseKey(key)
        except WindowsError:
            pass

    # Discord específicamente usa Squirrel
    discord_updater = (Path.home() / "AppData" / "Local"
                       / "Discord" / "Update.exe")
    if discord_updater.exists():
        findings.append({
            "path": str(discord_updater),
            "type": "DISCORD_SQUIRREL",
            "writable": os.access(str(discord_updater), os.W_OK),
        })

    return findings

# Extraído de: LibroBugBounty/cap-20-caso-epic.md
def find_epic_install():
    """Auto-detecta la ruta de instalacion de Epic Games."""
    import winreg
    reg_paths = [
        (winreg.HKEY_LOCAL_MACHINE,
         r"SOFTWARE\WOW6432Node\Epic Games\EpicGamesLauncher"),
        (winreg.HKEY_LOCAL_MACHINE,
         r"SOFTWARE\Epic Games\EpicGamesLauncher"),
        (winreg.HKEY_CURRENT_USER,
         r"SOFTWARE\Epic Games\EpicGamesLauncher"),
    ]
    for hive, key_path in reg_paths:
        try:
            key = winreg.OpenKey(hive, key_path)
            val, _ = winreg.QueryValueEx(key, "AppDataPath")
            winreg.CloseKey(key)
            # Navegar desde AppDataPath hasta el directorio
            # que contiene EpicGamesUpdater.exe
            target = locate_updater_from_base(val)
            if target:
                return target
        except (OSError, FileNotFoundError):
            pass
    # Fallback: rutas comunes en Program Files
    return scan_common_paths()

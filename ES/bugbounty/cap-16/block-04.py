# Extraído de: LibroBugBounty/cap-16-reconocimiento-surface.md
import winreg

def get_known_dlls():
    """Lee la lista de Known DLLs del registro del sistema."""
    known = set()
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\KnownDLLs"
        )
        i = 0
        while True:
            try:
                name, value, _ = winreg.EnumValue(key, i)
                # Los valores son nombres de DLL (ej: "kernel32.dll")
                known.add(value.lower())
                i += 1
            except WindowsError:
                break
        winreg.CloseKey(key)
    except WindowsError:
        # Fallback a lista hardcodeada si falla
        known = {"kernel32.dll", "user32.dll", "ntdll.dll"}
    return known

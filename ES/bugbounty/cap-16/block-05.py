# Extraído de: LibroBugBounty/cap-16-reconocimiento-surface.md
import pefile
from pathlib import Path

# DLLs protegidas por el mecanismo Known DLLs de Windows
KNOWN_DLLS = {
    "kernel32.dll", "user32.dll", "gdi32.dll", "advapi32.dll",
    "shell32.dll", "ole32.dll", "oleaut32.dll", "comctl32.dll",
    "ws2_32.dll", "psapi.dll", "msvcrt.dll", "ntdll.dll",
    "comdlg32.dll", "rpcrt4.dll", "secur32.dll", "shlwapi.dll",
    # ... (lista completa de ~50 DLLs)
}

def inventory_binaries(install_dir):
    """Inventario de EXEs y DLLs con análisis de imports."""
    exes = []
    dlls = []
    hijackable = []

    for item in Path(install_dir).rglob("*"):
        suffix = item.suffix.lower()
        if suffix == '.exe':
            exes.append(str(item))
            # Analizar imports
            try:
                pe = pefile.PE(str(item), fast_load=True)
                pe.parse_data_directories(
                    directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']]
                )
                if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
                    for entry in pe.DIRECTORY_ENTRY_IMPORT:
                        dll_name = entry.dll.decode().lower()
                        if dll_name not in KNOWN_DLLS:
                            # DLL no protegida — candidata a hijack
                            dll_in_dir = item.parent / dll_name
                            hijackable.append({
                                "exe": str(item),
                                "dll": dll_name,
                                "dll_exists_locally": dll_in_dir.exists(),
                                "exe_dir_writable": True,  # Ya lo sabemos
                            })
                pe.close()
            except Exception:
                pass

        elif suffix == '.dll':
            dlls.append(str(item))

    return {
        "total_files": sum(1 for _ in Path(install_dir).rglob("*")),
        "exes": len(exes),
        "dlls": len(dlls),
        "hijackable_imports": hijackable,
        "exe_list": exes,
    }

# Extraído de: LibroBugBounty/cap-06-dll-sideloading.md
# Paso 1: Extraer exports de la DLL original
# Ejecutado con Claude Code (datos pÃºblicos)
import pefile

def get_dll_exports(dll_path: str) -> list[dict]:
    """Extrae todos los exports de una DLL."""
    pe = pefile.PE(dll_path)
    exports = []

    if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
        for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
            if exp.name:
                exports.append({
                    "name": exp.name.decode(),
                    "ordinal": exp.ordinal,
                    "address": hex(exp.address),
                })

    return exports

# Exports de VERSION.dll:
# GetFileVersionInfoA
# GetFileVersionInfoByHandle
# GetFileVersionInfoExA
# GetFileVersionInfoExW
# GetFileVersionInfoSizeA
# GetFileVersionInfoSizeExA
# GetFileVersionInfoSizeExW
# GetFileVersionInfoSizeW
# GetFileVersionInfoW
# VerFindFileA
# VerFindFileW
# VerInstallFileA
# VerInstallFileW
# VerLanguageNameA
# VerLanguageNameW
# VerQueryValueA
# VerQueryValueW

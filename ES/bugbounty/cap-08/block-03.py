# Extraído de: LibroBugBounty/cap-08-analisis-drivers.md
def analyze_pe(filepath):
    """Análisis completo de un driver."""
    pe = pefile.PE(str(filepath))
    binary = lief.parse(str(filepath))

    # Verificar características de seguridad del PE
    dll_chars = pe.OPTIONAL_HEADER.DllCharacteristics
    security = {
        "ASLR":       bool(dll_chars & 0x0040),
        "DEP/NX":     bool(dll_chars & 0x0100),
        "CFG":        bool(dll_chars & 0x4000),  # Control Flow Guard
        "ForceInteg": bool(dll_chars & 0x0080),
    }

    # Extraer imports y clasificar por riesgo
    dangerous_found = []
    has_privilege_checks = False

    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        for imp in entry.imports:
            if imp.name:
                func = imp.name.decode()
                if func in DANGEROUS_IMPORTS:
                    dangerous_found.append(func)
                if func in PRIVILEGE_CHECKS:
                    has_privilege_checks = True

    # SEÑAL CRÍTICA: operaciones de memoria sin verificación
    has_mem_ops = any(f in dangerous_found
                      for f in ("MmMapIoSpace", "MmCopyMemory"))
    if has_mem_ops and not has_privilege_checks:
        risk = "CRITICAL: Operaciones de memoria SIN privilege checks"

    return dangerous_found, has_privilege_checks, risk

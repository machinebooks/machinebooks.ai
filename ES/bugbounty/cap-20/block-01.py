# Extraído de: LibroBugBounty/cap-20-caso-epic.md
def audit():
    """Auditoria de seguridad: permisos, DACL, firma."""
    # 1. Contar ficheros escribibles
    writable_dlls = sum(1 for f in EPIC_DIR.parent.parent.rglob("*.dll")
                        if f.is_file() and os.access(f, os.W_OK))
    writable_exes = sum(1 for f in EPIC_DIR.parent.parent.rglob("*.exe")
                        if f.is_file() and os.access(f, os.W_OK))

    # 2. Verificar DACL del servicio
    r = subprocess.run(
        ["sc.exe", "sdshow", "EpicGamesUpdater"],
        capture_output=True, text=True
    )
    dacl = r.stdout.strip()
    # BU = Builtin Users, RP = SERVICE_START
    can_start = "BU" in dacl and "RP" in dacl

    # 3. Verificar cuenta del servicio
    r2 = subprocess.run(
        ["sc.exe", "qc", "EpicGamesUpdater"],
        capture_output=True, text=True
    )
    is_system = "LocalSystem" in r2.stdout

    exploitable = writable_dlls > 0 and can_start and is_system
    return exploitable

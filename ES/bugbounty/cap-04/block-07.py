# Extraído de: LibroBugBounty/cap-04-electron-superficie.md
#!/usr/bin/env python3
"""
Detecta la versión de Electron de un ejecutable.
Busca la cadena de versión en las strings del binario.
"""
import re
from pathlib import Path

def detect_electron_version(exe_path: str) -> dict:
    """Detecta la versión de Electron y Chromium del ejecutable."""
    data = Path(exe_path).read_bytes()

    # Buscar versión de Chrome/Electron en strings
    # Patrón: "Chrome/XXX.0.XXXX.XX Electron/XX.X.X"
    text = data.decode("latin-1")

    electron_match = re.search(
        r'Electron/(\d+\.\d+\.\d+)', text
    )
    chrome_match = re.search(
        r'Chrome/(\d+\.\d+\.\d+\.\d+)', text
    )
    node_match = re.search(
        r'Node\.js/v(\d+\.\d+\.\d+)', text
    )

    result = {
        "electron": electron_match.group(1) if electron_match else None,
        "chromium": chrome_match.group(1) if chrome_match else None,
        "node": node_match.group(1) if node_match else None,
    }

    # Evaluar si la versión tiene soporte de fuses modernos
    if result["electron"]:
        major = int(result["electron"].split(".")[0])
        result["has_modern_fuses"] = major >= 20
        result["has_asar_integrity"] = major >= 22
        result["has_cookie_encryption"] = major >= 15
        result["eol"] = major < 28  # Versiones sin soporte

    return result

# Resultados de nuestra muestra:
# Discord: Electron 28.2.10, Chromium 120, Node 18.18.2
# Wand IDE: Electron 27.1.0, Chromium 118, Node 18.17.1
# VS Code: Electron 28.2.8, Chromium 120, Node 18.18.2
# Signal: Electron 28.0.0, Chromium 120, Node 18.18.2

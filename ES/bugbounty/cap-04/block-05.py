# Extraído de: LibroBugBounty/cap-04-electron-superficie.md
#!/usr/bin/env python3
"""
Extrae configuración de BrowserWindow del ASAR de una aplicación Electron.
Identifica ventanas con configuración insegura.
"""
import re
import json
import struct
from pathlib import Path

def extract_browser_window_config(asar_path: str) -> list[dict]:
    """Busca instancias de BrowserWindow y extrae su configuración."""
    # Extraer todos los ficheros .js del ASAR
    js_files = extract_all_js(asar_path)
    findings = []

    for filename, content in js_files.items():
        # Buscar new BrowserWindow({ ... })
        pattern = r'new\s+BrowserWindow\s*\(\s*\{([^}]{10,500})\}'
        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            config_text = match.group(1)

            # Extraer webPreferences
            wp_match = re.search(
                r'webPreferences\s*:\s*\{([^}]+)\}',
                config_text, re.DOTALL
            )
            if wp_match:
                prefs = wp_match.group(1)
                config = {
                    "file": filename,
                    "nodeIntegration": "nodeIntegration: true" in prefs
                                      or "nodeIntegration:true" in prefs,
                    "contextIsolation": "contextIsolation: false" not in prefs
                                       and "contextIsolation:false" not in prefs,
                    "sandbox": "sandbox: true" in prefs
                              or "sandbox:true" in prefs,
                }
                config["secure"] = (
                    not config["nodeIntegration"]
                    and config["contextIsolation"]
                )
                if not config["secure"]:
                    config["risk"] = "CRITICAL" if config["nodeIntegration"] else "HIGH"
                else:
                    config["risk"] = "LOW"
                findings.append(config)

    return findings

def extract_all_js(asar_path: str) -> dict:
    """Extrae todos los ficheros .js del ASAR."""
    # (Implementación usa el parser de ASAR del script anterior)
    # Devuelve dict de {filename: content_string}
    pass  # Implementación omitida por brevedad

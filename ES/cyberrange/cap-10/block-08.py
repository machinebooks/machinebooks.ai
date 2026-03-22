# Extraído de: LibroCyberrange/cap-10-servicios-proxmox.md
# Ejemplo didáctico: inicialización del Manager
# Patrón: backend/services/proxmox_sdk_manager.py

class ProxmoxSDKManager:
    """
    ARQUITECTURA:
    1. PROXMOX = Fuente de VERDAD
    2. MySQL   = SOLO MIRROR/CACHE
    3. Hooks   = UNICOS que escriben en MySQL
    """

    def __init__(self, db: Session):
        self.db = db
        self._live_sdk: Optional[ProxmoxSDKService] = None
        self._vnc_sdk: Optional[ProxmoxSDKService] = None
        self._sync_status = {
            'is_syncing': False,
            'last_sync_time': None,
            'sync_progress': 0,
            'sync_message': ''
        }
        # Cooldown: 15 segundos mínimo entre sincronizaciones
        self._last_sync_timestamps = {
            'vms': None, 'templates': None,
            'general': None, 'vm_status': None
        }
        self._sync_cooldown_seconds = 15

    def _get_live_sdk(self) -> ProxmoxSDKService:
        """Instancia perezosa del SDK para datos en tiempo real."""
        if self._live_sdk is None:
            self._live_sdk = create_proxmox_sdk_service()
        return self._live_sdk

    def _get_vnc_sdk(self) -> ProxmoxSDKService:
        """SDK dedicado para VNC con token de permisos reducidos."""
        if self._vnc_sdk is None:
            self._vnc_sdk = create_proxmox_sdk_service(use_vnc_token=True)
        return self._vnc_sdk

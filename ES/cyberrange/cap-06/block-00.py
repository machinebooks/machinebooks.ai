# Extraído de: LibroCyberrange/cap-06-proxmox-virtualizacion.md
# Ejemplo didáctico: patrones/backend/services/proxmox_manager.py
# Inicialización dual: token para operaciones, ticket para VNC

class ProxmoxManager:
    """
    Manager que mantiene dos conexiones al hipervisor:
    - SDK con token de API para operaciones programáticas
    - SDK con ticket para acceso a consolas VNC
    """

    def __init__(self, db: Session):
        self.db = db
        self._live_sdk = None   # Token API: operaciones CRUD
        self._vnc_sdk = None    # Ticket auth: consolas VNC

    def _get_live_sdk(self) -> ProxmoxSDKService:
        """SDK con token de API para operaciones de larga duración"""
        if self._live_sdk is None:
            self._live_sdk = create_proxmox_sdk_service()
        return self._live_sdk

    def _get_vnc_sdk(self) -> ProxmoxSDKService:
        """SDK con ticket para acceso a consolas VNC"""
        if self._vnc_sdk is None:
            self._vnc_sdk = create_proxmox_sdk_service(use_vnc_token=True)
        return self._vnc_sdk

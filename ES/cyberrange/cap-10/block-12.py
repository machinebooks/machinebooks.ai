# Extraído de: LibroCyberrange/cap-10-servicios-proxmox.md
# Ejemplo didáctico: métricas en tiempo real
# Patrón: backend/services/proxmox_live_service.py

class ProxmoxLiveService:
    """Conexión directa a Proxmox para datos en tiempo real."""

    def __init__(self):
        self.proxmox = None
        self._connect()

    def _connect(self):
        """Conexión con autenticación por token (preferida)
        o por usuario/password.
        verify_ssl configurable: True por defecto (producción).
        Solo False en lab con certificados autofirmados."""
        ssl_verify = settings.proxmox_ssl_verify  # True por defecto
        if self.token_id and self.token_secret:
            self.proxmox = ProxmoxAPI(
                host=self.host, port=self.port,
                token_name=self.token_id,
                token_value=self.token_secret,
                verify_ssl=ssl_verify, timeout=30
            )
        else:
            self.proxmox = ProxmoxAPI(
                host=self.host, port=self.port,
                user=self.user, password=self.password,
                verify_ssl=ssl_verify, timeout=30
            )
        # Verificar conexión
        version = self.proxmox.version.get()

    async def get_vm_status(self, node: str, vmid: int) -> Dict:
        """Estado actual de una VM: CPU, memoria, red, disco."""
        loop = asyncio.get_event_loop()
        status = await loop.run_in_executor(
            None,
            lambda: self.proxmox.nodes(node).qemu(vmid) \
                .status.current.get()
        )
        return {
            'vmid': vmid,
            'status': status.get('status', 'unknown'),
            'cpu': status.get('cpu', 0),
            'memory': status.get('mem', 0),
            'maxmem': status.get('maxmem', 0),
            'disk_read': status.get('diskread', 0),
            'disk_write': status.get('diskwrite', 0),
            'network_in': status.get('netin', 0),
            'network_out': status.get('netout', 0),
            'last_updated': 'live'  # Marca de datos en tiempo real
        }

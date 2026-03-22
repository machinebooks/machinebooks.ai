# Extraído de: LibroCyberrange/cap-05-arquitectura.md
# Ejemplo didáctico: patrones/services/auto_sync.py
# Sincronización periódica Proxmox → MySQL

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

class AutoSyncService:
    """
    Reconcilia MySQL con Proxmox cada N minutos.
    - Lee el estado real de Proxmox (nodos, VMs, templates)
    - Actualiza los registros existentes en MySQL
    - NO crea ni elimina registros (eso lo hacen las operaciones)
    """

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.sync_stats = {
            "total_syncs": 0,
            "successful": 0,
            "failed": 0,
            "last_error": None
        }

    def start(self):
        self.scheduler.add_job(
            self.sync_all_clusters,
            trigger=IntervalTrigger(minutes=15),
            id="proxmox_auto_sync",
            replace_existing=True
        )
        self.scheduler.start()

    async def sync_all_clusters(self):
        """Sincroniza todos los clusters registrados."""
        clusters = db.query(ProxmoxCluster).all()
        for cluster in clusters:
            try:
                # Obtener estado real de Proxmox
                nodes = proxmox_sdk.proxmox(type="all", action="nodes")
                vms = proxmox_sdk.proxmox(type="all", action="list")

                # Actualizar MySQL (solo existentes, no crear/eliminar)
                self._sync_nodes(cluster.id, nodes["items"])
                self._sync_vms(cluster.id, vms["items"])

                self.sync_stats["successful"] += 1
            except Exception as e:
                self.sync_stats["failed"] += 1
                self.sync_stats["last_error"] = str(e)

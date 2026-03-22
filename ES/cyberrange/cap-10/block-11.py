# Extraído de: LibroCyberrange/cap-10-servicios-proxmox.md
# Ejemplo didáctico: servicio de sincronización automática
# Patrón: backend/services/auto_sync_service.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

class AutoSyncService:
    """Sincronización automática en background."""

    def __init__(self):
        self.scheduler = None
        self.is_running = False
        self.sync_stats = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'last_error': None
        }

    async def sync_all_clusters(self):
        """Sincronizar todos los clusters registrados."""
        if self.is_running:
            return  # Evitar ejecución concurrente

        self.is_running = True
        start_time = datetime.now()

        try:
            clusters = db.query(ProxmoxCluster).all()
            for cluster in clusters:
                # Timeout preventivo: si ya pasaron 45s, parar
                if (datetime.now() - start_time).seconds > 45:
                    break

                # Sincronizar VMs (max 20s por cluster)
                await asyncio.wait_for(
                    manager.sync_vms(cluster.id), timeout=20
                )
                # Sincronizar Templates (max 15s por cluster)
                await asyncio.wait_for(
                    manager.sync_templates(cluster.id), timeout=15
                )

            self.sync_stats['successful_syncs'] += 1
        except asyncio.TimeoutError:
            self.sync_stats['failed_syncs'] += 1
        finally:
            self.is_running = False

    def start(self):
        """Iniciar scheduler: sync cada 2 minutos."""
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            func=lambda: asyncio.run(self.sync_all_clusters()),
            trigger=IntervalTrigger(seconds=120),
            id='auto_sync_proxmox',
            max_instances=1,   # Solo una instancia simultánea
            coalesce=True,     # Combinar ejecuciones perdidas
            misfire_grace_time=30
        )
        self.scheduler.start()

        # Sync inicial 10 segundos después del arranque
        self.scheduler.add_job(
            func=lambda: asyncio.run(self.sync_all_clusters()),
            trigger='date',
            run_date=datetime.now() + timedelta(seconds=10),
            id='initial_sync'
        )

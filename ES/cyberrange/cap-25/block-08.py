# Extraído de: LibroCyberrange/cap-25-despliegue-produccion.md
# Ejemplo didáctico: patrones/backend/auto_sync.py

class AutoSyncService:
    """Sincronización periódica Proxmox → MySQL con APScheduler."""

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
        """Sincroniza VMs y templates de todos los clústeres."""
        if self.is_running:
            return                       # Evitar ejecuciones solapadas

        self.is_running = True
        start_time = datetime.now()

        try:
            db = self.session_factory()
            manager = get_proxmox_sdk_manager(db)
            clusters = db.query(ProxmoxCluster).all()

            for cluster in clusters:
                # Timeout preventivo: si llevamos >45s, parar
                if (datetime.now() - start_time).total_seconds() > 45:
                    break

                # Sincronizar VMs (timeout 20s por cluster)
                vm_result = await asyncio.wait_for(
                    manager.sync_vms(cluster.id), timeout=20
                )

                # Sincronizar Templates (timeout 15s por cluster)
                template_result = await asyncio.wait_for(
                    manager.sync_templates(cluster.id), timeout=15
                )

        finally:
            self.is_running = False
            db.close()

    def start(self):
        """Inicia el scheduler con ejecución cada 2 minutos."""
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            func=lambda: asyncio.run(self.sync_all_clusters()),
            trigger=IntervalTrigger(seconds=120),
            id='auto_sync_proxmox',
            max_instances=1,             # Solo una ejecución simultánea
            coalesce=True,               # Combinar ejecuciones perdidas
            misfire_grace_time=30        # Gracia de 30s para ejecuciones retrasadas
        )
        self.scheduler.start()

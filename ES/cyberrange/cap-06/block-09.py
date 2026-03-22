# Extraído de: LibroCyberrange/cap-06-proxmox-virtualizacion.md
# Ejemplo didáctico: patrones/backend/services/auto_sync_service.py
# Servicio de sincronización automática Proxmox → MySQL

class AutoSyncService:
    """
    Mantiene MySQL sincronizado con Proxmox automáticamente.
    Ejecuta periódicamente con protección contra ejecuciones solapadas.
    """

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
        """Sincronizar todos los clusters registrados"""
        if self.is_running:
            logger.warning("Sincronización ya en curso, saltando ciclo")
            return

        self.is_running = True
        start_time = datetime.now()

        try:
            db = self.session_factory()
            manager = get_proxmox_sdk_manager(db)
            clusters = db.query(ProxmoxCluster).all()

            for cluster in clusters:
                # Timeout preventivo: si llevamos más de 45s, parar
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed > 45:
                    logger.warning(f"Timeout preventivo en {cluster.name}")
                    break

                # Sincronizar VMs (timeout individual: 20s)
                vm_result = await asyncio.wait_for(
                    manager.sync_vms(cluster.id),
                    timeout=20
                )

                # Sincronizar templates (timeout individual: 15s)
                template_result = await asyncio.wait_for(
                    manager.sync_templates(cluster.id),
                    timeout=15
                )

            db.close()
        finally:
            self.is_running = False

    def start(self):
        """Iniciar scheduler con APScheduler"""
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            func=lambda: asyncio.run(self.sync_all_clusters()),
            trigger=IntervalTrigger(seconds=120),
            id='auto_sync_proxmox',
            max_instances=1,     # Solo una instancia simultánea
            coalesce=True,       # Combinar ejecuciones perdidas
            misfire_grace_time=30
        )
        self.scheduler.start()

# Extraído de: LibroCyberrange/cap-11-base-datos.md
class ProxmoxSyncLog(Base):
    """Registro de cada sincronización con Proxmox."""
    __tablename__ = "proxmox_sync_log"
    id = Column(Integer, primary_key=True)
    cluster_id = Column(Integer, ForeignKey("proxmox_cluster.id"))
    sync_type = Column(Enum('full', 'incremental', 'manual'), nullable=False)
    status = Column(Enum('started', 'success', 'error', 'partial'))

    # Estadísticas de sincronización
    nodes_synced = Column(Integer, default=0)
    vms_synced = Column(Integer, default=0)
    templates_synced = Column(Integer, default=0)
    snapshots_synced = Column(Integer, default=0)

    # Diagnóstico
    changes_detected = Column(JSON)    # Qué cambió desde la última sincronización
    errors = Column(JSON)              # Errores ocurridos durante la sincronización
    duration_seconds = Column(Integer)

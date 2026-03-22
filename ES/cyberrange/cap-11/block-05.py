# Extraído de: LibroCyberrange/cap-11-base-datos.md
class ProxmoxCluster(Base):
    """Cluster de Proxmox registrado en la plataforma."""
    __tablename__ = "proxmox_cluster"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    host = Column(String(255), nullable=False)       # IP o FQDN
    port = Column(Integer, default=8006)
    username = Column(String(128), nullable=False)
    password = Column(String(255), nullable=False)    # Encriptado en reposo
    api_token_id = Column(String(128))               # Autenticación por token (preferida)
    api_token_secret = Column(String(255))
    ssl_verify = Column(Boolean, default=True)

    # Estado y recursos globales del cluster
    status = Column(Enum('online', 'offline', 'maintenance'), default='offline')
    version = Column(String(32))                     # Versión de Proxmox VE
    total_cpu_cores = Column(Integer)
    total_memory_mb = Column(BigInteger)
    total_storage_gb = Column(BigInteger)
    last_sync = Column(DateTime)

class ProxmoxNode(Base):
    """Nodo individual dentro de un cluster."""
    __tablename__ = "proxmox_node"
    id = Column(Integer, primary_key=True)
    cluster_id = Column(Integer, ForeignKey("proxmox_cluster.id"), nullable=False)
    name = Column(String(128), nullable=False)

    # Recursos del nodo — actualizados en cada sincronización
    cpu_cores = Column(Integer)
    cpu_usage_percent = Column(SmallInteger)
    memory_total_mb = Column(BigInteger)
    memory_used_mb = Column(BigInteger)
    storage_total_gb = Column(BigInteger)
    storage_used_gb = Column(BigInteger)

    # Estado y red
    status = Column(Enum('online', 'offline', 'unknown'), default='unknown')
    uptime = Column(BigInteger)          # Segundos
    ip_address = Column(String(15))
    network_in = Column(BigInteger)      # Bytes recibidos acumulados
    network_out = Column(BigInteger)     # Bytes enviados acumulados
    last_sync = Column(DateTime)

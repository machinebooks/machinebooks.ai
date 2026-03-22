# Extraído de: LibroCyberrange/cap-11-base-datos.md
class ProxmoxTemplate(Base):
    """Templates disponibles en Proxmox para clonación."""
    __tablename__ = "proxmox_template"
    id = Column(Integer, primary_key=True)
    cluster_id = Column(Integer, ForeignKey("proxmox_cluster.id"))
    node_id = Column(Integer, ForeignKey("proxmox_node.id"))
    vmid = Column(Integer, nullable=False)    # VMID del template en Proxmox
    name = Column(String(128), nullable=False)

    # Configuración del template
    os_type = Column(String(64))              # linux, windows
    os_family = Column(String(32))            # debian, ubuntu, centos, windows
    cpu_cores = Column(Integer)
    memory_mb = Column(Integer)
    disk_size_gb = Column(Integer)

    # Cloud-init para configuración automática post-clonación
    cloud_init_enabled = Column(Boolean, default=False)
    default_cloud_init = Column(JSON)

    # Categorización para búsqueda en la interfaz
    category = Column(String(64))             # server, desktop, security
    tags = Column(JSON)
    installed_software = Column(JSON)         # Software preinstalado en el template
    default_credentials = Column(JSON)        # Credenciales por defecto (encriptadas)

    # Estadísticas de uso
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime)

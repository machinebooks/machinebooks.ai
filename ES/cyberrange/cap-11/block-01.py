# Extraído de: LibroCyberrange/cap-11-base-datos.md
class Workzone(Base):
    """Espacio aislado de trabajo con red propia y recursos dedicados."""
    __tablename__ = "workzone"
    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, unique=True, nullable=True)  # ID de aplicación (1-15)
    name = Column(String(128))
    owner_user = Column(Integer, nullable=True)

    # Límites de recursos — cada workzone tiene cuota
    cpu_limit = Column(Integer)      # Cores máximos
    memory_limit = Column(Integer)   # MB máximos
    storage_limit = Column(Integer)  # GB máximos

    # Control de zonas: una workzone puede estar en modo gaming o cyberrange
    current_zone = Column(Enum('none', 'gaming', 'cyberrange'), default='none')
    zone_started_at = Column(DateTime)
    zone_ttl_hours = Column(Integer, default=4)  # Tiempo de vida máximo
    auto_cleanup_at = Column(DateTime)           # Limpieza automática

    # Aislamiento de red — cada workzone obtiene su propia red virtual
    vlan_id = Column(Integer, nullable=True, unique=True)  # Tag VLAN (100-999)
    network_cidr = Column(String(32))    # e.g. "10.1.0.0/24"
    gateway_ip = Column(String(45))      # e.g. "10.1.0.1"
    dhcp_start = Column(String(45))      # Inicio del rango DHCP
    dhcp_end = Column(String(45))        # Fin del rango DHCP
    pfsense_ip = Column(String(45))      # IP del firewall de la workzone
    pfsense_vmid = Column(Integer)       # VMID de pfSense en Proxmox
    internet_enabled = Column(Boolean, default=False)  # Internet deshabilitado por defecto

    # Escenario activo
    scenario_id = Column(Integer, ForeignKey("scenario.id"), nullable=True)
    status = Column(Enum('active', 'inactive', 'occupied'), default='active')

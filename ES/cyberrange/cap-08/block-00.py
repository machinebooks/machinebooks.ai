# Extraído de: LibroCyberrange/cap-08-workzones.md
# Ejemplo didáctico: models.py — Modelo Workzone

class Workzone(Base):
    __tablename__ = "workzone"
    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, unique=True, nullable=True)   # ID único (1-15)
    name = Column(String(128))
    owner_user = Column(Integer, nullable=True)

    # --- Presupuesto de recursos ---
    cpu_limit = Column(Integer)          # Cores máximos
    memory_limit = Column(Integer)       # MB máximos
    storage_limit = Column(Integer)      # GB máximos

    # --- Modo de operación y TTL ---
    current_zone = Column(
        Enum('none', 'gaming', 'cyberrange'), default='none'
    )
    zone_started_at = Column(DateTime)          # Inicio de la zona activa
    zone_ttl_hours = Column(Integer, default=4) # TTL en horas
    auto_cleanup_at = Column(DateTime)          # Cuándo se limpia

    # --- Aislamiento de red (pfSense dedicado) ---
    vlan_id = Column(Integer, unique=True)          # VLAN tag (100-999)
    network_cidr = Column(String(32))               # e.g. "10.100.0.0/24"
    gateway_ip = Column(String(45))                 # e.g. "10.100.0.1"
    dhcp_start = Column(String(45))                 # e.g. "10.100.0.100"
    dhcp_end = Column(String(45))                   # e.g. "10.100.0.200"
    pfsense_ip = Column(String(45))                 # IP del pfSense
    pfsense_api_key = Column(String(255))           # API key pfSense
    pfsense_vmid = Column(Integer)                  # VMID en Proxmox
    pfsense_rule_ids = Column(JSON)                 # IDs de reglas creadas
    internet_enabled = Column(Boolean, default=False)

    # --- Escenario activo ---
    scenario_id = Column(Integer, ForeignKey("scenario.id"))

    # --- Estado ---
    status = Column(
        Enum('active', 'inactive', 'occupied'), default='active'
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

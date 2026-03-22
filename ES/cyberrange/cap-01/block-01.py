# Extraído de: LibroCyberrange/cap-01-que-es-cyber-range.md
# Modelo simplificado de workzone
# Ejemplo didáctico: patrones/workzone/models.py

class Workzone(Base):
    __tablename__ = "workzone"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    app_id = Column(Integer, unique=True)  # Identificador único 1-99

    # Aislamiento de red
    vlan_id = Column(Integer, unique=True)  # VLAN dedicada
    network_cidr = Column(String(18))       # Ej: "10.1.0.0/24"
    pfsense_vmid = Column(Integer)          # Firewall dedicado
    internet_enabled = Column(Boolean, default=False)

    # Límites de recursos
    max_cpu = Column(Integer, default=16)
    max_memory_gb = Column(Integer, default=32)
    max_storage_gb = Column(Integer, default=500)
    max_vms = Column(Integer, default=20)

    # Ciclo de vida
    zone_ttl_hours = Column(Integer, default=24)
    auto_cleanup_at = Column(DateTime)
    current_zone = Column(Enum("gaming", "cyberrange", "none"))

    # Relaciones
    scenario_id = Column(Integer, ForeignKey("scenario.id"))
    users = relationship("User", back_populates="workzone")

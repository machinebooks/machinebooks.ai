# Extraído de: LibroCyberrange/cap-13-escenarios-topologias.md
# backend/models.py — Modelo de plantilla de escenarios
class ScenarioTemplate(Base):
    """Plantilla reutilizable de escenario con toda la configuración
    necesaria para desplegar un laboratorio completo."""
    __tablename__ = "scenario_template"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    category = Column(String(64))          # red-team, blue-team, ot, forensic, crisis
    difficulty = Column(
        Enum('beginner', 'intermediate', 'advanced', 'expert'),
        default='beginner'
    )

    # Los cuatro bloques de configuración
    topology_config = Column(JSON)   # Zonas de red, conexiones, firewalls
    vm_configs = Column(JSON)        # Máquinas virtuales y sus servicios
    network_configs = Column(JSON)   # VLANs, subredes, gateways
    security_configs = Column(JSON)  # Flags, vulnerabilidades, evaluación

    # Metadatos
    author_id = Column(Integer, ForeignKey("user.id"))
    is_public = Column(Boolean, default=False)
    version = Column(String(16), default="1.0")
    tags = Column(JSON)              # Para búsqueda y filtrado

    # Tiempos estimados (minutos)
    estimated_deploy_time = Column(Integer)
    estimated_destroy_time = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Extraído de: LibroCyberrange/cap-11-base-datos.md
class Challenge(Base):
    """Reto individual del Cyber Range."""
    __tablename__ = "challenge"
    id = Column(Integer, primary_key=True)
    title = Column(String(128))
    type = Column(Enum('ctf', 'crisis', 'guided', 'escape'))
    difficulty = Column(Enum('beginner', 'easy', 'medium', 'hard', 'extreme'),
                        default='medium')
    max_points = Column(Integer)
    base_topology_id = Column(Integer, ForeignKey("topology_design.id"))

    # --- Campos enterprise ---
    status = Column(Enum('draft', 'published', 'archived'), default='draft')
    category = Column(String(64))             # "web", "crypto", "forensics"
    tags = Column(JSON)                       # ["web", "crypto", "forensics"]
    time_limit_minutes = Column(Integer)      # Límite de tiempo por participante
    max_attempts = Column(Integer)            # Máximo intentos de flag
    prerequisite_ids = Column(JSON)           # [challenge_id, ...] — prerrequisitos

    # --- Flags dinámicas por usuario ---
    flag_type = Column(Enum('static', 'dynamic'), default='static')
    template_vmid = Column(Integer)           # VMID del template en Proxmox
    template_type = Column(Enum('qemu', 'lxc'), default='lxc')
    playbook_id = Column(Integer)             # Playbook Ansible para setup
    setup_playbook_yaml = Column(Text)        # Playbook YAML inline (alternativa)

    # Relación con MITRE ATT&CK
    mitre_techniques = relationship("ChallengeMitreTechnique",
                                     back_populates="challenge", lazy="select")

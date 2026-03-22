# Extraído de: LibroCyberrange/cap-15-ataques-defensa.md
class ActionTemplate(Base):
    __tablename__ = "action_template"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    default_cmd = Column(Text)           # Comando parametrizable: "{target}"
    severity = Column(SmallInteger)      # 1-5 (info → critical)
    complexity = Column(SmallInteger)    # 1-5 (trivial → expert)

    # Impacto CIA
    integrity = Column(SmallInteger)      # 0-3
    availability = Column(SmallInteger)   # 0-3
    confidentiality = Column(SmallInteger) # 0-3

    # Clasificación MITRE ATT&CK
    mitre_technique_id = Column(String(16))   # "T1595", "T1059.001"
    mitre_tactic = Column(String(64))         # "Reconnaissance", "Execution"
    kill_chain_phase = Column(String(64))     # "Delivery", "Exploitation"

    asset_requirements = Column(JSON)    # VMs/herramientas necesarias
    tags = Column(JSON)                  # ["network", "windows", "ad"]
    created_at = Column(DateTime, default=datetime.utcnow)

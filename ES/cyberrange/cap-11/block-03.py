# Extraído de: LibroCyberrange/cap-11-base-datos.md
class ChallengeInstance(Base):
    """Participación de un usuario en un reto específico."""
    __tablename__ = "challenge_instance"
    id = Column(Integer, primary_key=True)
    challenge_id = Column(Integer, ForeignKey("challenge.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    scenario_id = Column(Integer, ForeignKey("scenario.id"))
    state = Column(Enum('open', 'done'), default='open')
    score = Column(Integer, default=0)

    # Campos para flags dinámicas: cada instancia tiene su propia VM
    vmid = Column(Integer)                    # VMID de la instancia clonada
    vm_type = Column(Enum('qemu', 'lxc'))
    ip_address = Column(String(45))           # IP de la instancia del usuario
    flag_value = Column(String(128))          # Flag única para este usuario
    hash_seed = Column(String(64))            # Seed usado para generar la flag
    expires_at = Column(DateTime)             # Cuándo expira la instancia
    vm_status = Column(String(20), default='none')  # none→cloning→running→stopped→destroyed

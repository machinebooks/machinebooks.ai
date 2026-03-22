# Extraído de: LibroCyberrange/cap-11-base-datos.md
class CtfFlag(Base):
    """Flag individual dentro de un reto."""
    __tablename__ = "ctf_flag"
    id = Column(Integer, primary_key=True)
    challenge_id = Column(Integer, ForeignKey("challenge.id"))
    flag_token = Column(String(64), unique=True)  # El valor de la flag
    points = Column(Integer, default=100)
    kind = Column(Enum('static', 'vm', 'container', 'dynamic'), default='static')

class CtfHint(Base):
    """Pista desbloqueable con penalización de puntos."""
    __tablename__ = "ctf_hint"
    id = Column(Integer, primary_key=True)
    flag_id = Column(Integer, ForeignKey("ctf_flag.id"))
    text = Column(Text)
    penalty_pct = Column(Integer, default=10)  # Porcentaje de puntos que se pierde
    order_idx = Column(Integer)                # Orden de revelación progresiva

class CtfHintUse(Base):
    """Registro de cuándo un usuario desbloqueó una pista."""
    __tablename__ = "ctf_hint_use"
    id = Column(Integer, primary_key=True)
    hint_id = Column(Integer, ForeignKey("ctf_hint.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    instance_id = Column(Integer, ForeignKey("challenge_instance.id"))
    used_at = Column(DateTime, default=datetime.utcnow)

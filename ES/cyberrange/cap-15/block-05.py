# Extraído de: LibroCyberrange/cap-15-ataques-defensa.md
class AttackLog(Base):
    __tablename__ = "attack_log"
    id = Column(Integer, primary_key=True)
    attack_id = Column(Integer,
                       ForeignKey("attack_execution.id", ondelete="CASCADE"))
    ts = Column(DateTime, default=datetime.utcnow)
    log_line = Column(Text)

# Extraído de: LibroCyberrange/cap-14-equipos-competicion.md
class ScoreLog(Base):
    __tablename__ = "score_log"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    points = Column(Integer)
    reason = Column(String(128))  # Motivo legible
    ts = Column(DateTime, default=datetime.utcnow)

# Extraído de: LibroDevSecOps/cap-23-excepciones-deuda.md
class ExceptionReview(Base):
    """Registro de cada revisión periódica de una excepción."""
    __tablename__ = "exception_reviews"

    id = Column(Integer, primary_key=True)
    exception_id = Column(Integer, ForeignKey("security_exceptions.id"))
    reviewed_at = Column(DateTime, default=datetime.utcnow)
    reviewer = Column(String(128), nullable=False)  # agente o humano
    conditions_changed = Column(JSON, nullable=True)
    recommendation = Column(String(32), nullable=False)  # renew, escalate, resolve
    notes = Column(Text, nullable=True)

    exception = relationship("SecurityException", back_populates="reviews")

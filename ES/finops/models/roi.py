# Extraído de: LibroFinOps/cap-17-roi-humanbaseline.md
# models/roi.py — Registro de cada tarea completada con IA
class TaskCompletionLog(Base):
    """
    Registro unitario de tarea completada. ROI calculado al insertar.
    """
    __tablename__ = "task_completion_log"

    id = Column(Integer, primary_key=True)
    baseline_config_id = Column(Integer, ForeignKey("human_baseline_config.id"))
    llm_usage_log_id = Column(Integer, ForeignKey("llm_usage_log.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tenant_id = Column(Integer, ForeignKey("tenants.id"))

    task_type = Column(String(100), nullable=False)
    accepted = Column(Boolean, default=True)           # ¿el usuario aceptó la salida?
    llm_cost_eur = Column(Float, nullable=False)       # coste real del token en €
    human_value_eur = Column(Float)                    # valor liberado calculado
    roi_gross = Column(Float)                          # ROI bruto sin correcciones
    roi_adjusted = Column(Float)                       # ROI con overhead y factor captura
    completed_at = Column(DateTime, default=datetime.utcnow)
    context = Column(Text)                             # metadatos adicionales (JSON)

    baseline_config = relationship("HumanBaselineConfig", back_populates="completions")

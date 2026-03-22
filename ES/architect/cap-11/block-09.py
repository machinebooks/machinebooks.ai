# Extraído de: LibroTecnico/cap-11-integracion-llms.md
# Ejemplo didáctico: patrones/ai_service/models/roi_tracker.py
class HumanBaselineConfig(Base):
    """
    Tiempo humano estimado por tipo de tarea.
    Configurable desde panel Admin para ajustar a la realidad de la organización.
    """
    __tablename__ = "human_baseline_config"

    service_type = Column(String(64), primary_key=True)
    task_name = Column(String(128))
    human_time_minutes = Column(Float, nullable=False)  # Tiempo humano promedio
    human_hourly_cost_eur = Column(Float, default=65.0) # Coste/hora del perfil tipo
    complexity_factor = Column(Float, default=1.0)      # Para tareas con varianza alta

    # Ejemplos reales configurados en la plataforma:
    # document_analyzer: 480 min (8 horas), complexity_factor=1.5
    # proposal_generator: 2400 min (40 horas), complexity_factor=2.0
    # cv_analyzer: 45 min, complexity_factor=0.8
    # opportunity_scorer: 120 min (2 horas), complexity_factor=1.0


class TaskCompletionLog(Base):
    """
    Log de tareas completadas con cálculo de ROI.
    Se crea cuando una tarea de IA finaliza con éxito.
    """
    __tablename__ = "task_completion_log"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    service_type = Column(String(64), index=True)
    user_id = Column(String(36), index=True)

    # Métricas de IA
    ai_duration_seconds = Column(Float)
    llm_cost_eur = Column(Float)           # Del LLMUsageLog correspondiente

    # ROI calculado
    human_time_baseline_minutes = Column(Float)
    time_saved_minutes = Column(Float)     # baseline - ai_duration/60
    money_saved_eur = Column(Float)        # time_saved * hourly_cost / 60

    # Calidad del resultado
    quality_score = Column(Float)          # De LLMQualityScore si disponible
    user_rating = Column(Integer)          # 1-5 del feedback loop
    was_accepted = Column(Boolean)         # ¿El usuario aceptó el resultado?

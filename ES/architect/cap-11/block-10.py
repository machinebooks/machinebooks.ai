# Extraído de: LibroTecnico/cap-11-integracion-llms.md
# Ejemplo didáctico: patrones/ai_service/models/quality_score.py
class LLMQualityScore(Base):
    """
    Puntuación de calidad por tarea completada.
    Combina evaluación automática y feedback humano.
    """
    __tablename__ = "llm_quality_score"

    id = Column(Integer, primary_key=True)
    usage_log_id = Column(Integer, ForeignKey("llm_usage_log.id"), index=True)
    service_type = Column(String(64), index=True)
    model_id = Column(String(64))
    prompt_id = Column(String(64))  # Para correlacionar con versión de prompt

    # 7 métricas de calidad (0.0-1.0 cada una)
    hallucination_score = Column(Float)    # Inverso: 0=no alucinación, 1=alta
    groundedness_score = Column(Float)     # Qué tan anclado está en el contexto
    relevance_score = Column(Float)        # Relevancia de la respuesta
    coherence_score = Column(Float)        # Coherencia interna del texto
    bias_score = Column(Float)             # Nivel de sesgo detectado
    toxicity_score = Column(Float)         # Contenido dañino
    pii_leak_score = Column(Float)         # PII en el output

    # Score compuesto (ponderado según perfil del servicio)
    composite_score = Column(Float)

    # Feedback humano
    user_rating = Column(Integer)          # 1-5 estrellas
    user_feedback_text = Column(Text)
    expert_review = Column(Boolean)        # Revisión manual por experto

    evaluated_at = Column(DateTime, default=datetime.utcnow)
    evaluation_method = Column(String(16)) # "auto", "user", "expert"

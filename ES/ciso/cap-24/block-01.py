# Extraído de: LibroCISO/cap-24-calidad-ia.md
class LLMQualityScore(Base):
    """Evaluación de calidad semántica de respuestas LLM.

    Se calcula por muestreo o para servicios críticos (agentes
    que generan entregables regulatorios). No se evalúa el 100%
    de las llamadas — el coste de evaluación sería prohibitivo.
    """
    __tablename__ = 'llm_quality_scores'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    usage_log_id = Column(BigInteger, ForeignKey('llm_usage_logs.id'))

    service_type = Column(String(50), nullable=False, index=True)

    # Alucinación: 0.0 = sin alucinación, 1.0 = alucinación total
    # Se calcula con un modelo evaluador (claude-haiku-4-5)
    hallucination_score = Column(Float, nullable=True)

    # Groundedness: ¿la respuesta se basa en el contexto RAG?
    # 1.0 = completamente fundamentada, 0.0 = sin relación con fuentes
    groundedness_score = Column(Float, nullable=True)

    # Relevancia: ¿la respuesta es pertinente a la pregunta?
    relevance_score = Column(Float, nullable=True)

    # Coherencia interna del texto generado
    coherence_score = Column(Float, nullable=True)

    # Sesgo detectado
    bias_detected = Column(Boolean, default=False)
    bias_categories = Column(JSON, nullable=True)  # ['sector', 'size']
    bias_score = Column(Float, nullable=True)

    # Seguridad
    pii_detected = Column(Boolean, default=False)

    # Feedback humano (1-5, lo pone el CISO/DPO)
    human_rating = Column(Integer, nullable=True)

    # Qué método de evaluación se usó
    evaluation_method = Column(String(50), nullable=True)
    # 'llm_judge', 'rule_based', 'human', 'hybrid'
    evaluator_model = Column(String(100), nullable=True)
    # 'claude-haiku-4-5' cuando el evaluador es otro LLM

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

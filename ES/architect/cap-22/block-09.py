# Extraído de: LibroTecnico/cap-22-observabilidad.md
class LLMUsageLog(db.Model):
    """Log de cada llamada a un modelo LLM.

    Fuente de verdad para análisis de costes, calidad y rendimiento.
    Se correlaciona con TaskCompletionLog para análisis de ROI por modelo.
    """
    __tablename__ = 'llm_usage_logs'
    __bind_key__ = 'platform_core'

    id = db.Column(db.Integer, primary_key=True)

    # Trazabilidad
    user_id = db.Column(db.Integer, nullable=True)
    session_id = db.Column(db.String(100), nullable=True)
    request_id = db.Column(db.String(100), nullable=True)  # Correlación con HTTP logs

    # Modelo utilizado
    provider = db.Column(db.String(50), nullable=False)  # 'anthropic', 'azure_openai', etc.
    model = db.Column(db.String(100), nullable=False)     # 'claude-sonnet-4-6', etc.
    service_type = db.Column(db.String(100), nullable=True)
    # 'document_analysis', 'proposal_generation', 'cv_analyzer', 'rag_query'

    # Tokens
    prompt_tokens = db.Column(db.Integer, nullable=False)
    completion_tokens = db.Column(db.Integer, nullable=False)
    total_tokens = db.Column(db.Integer, nullable=False)

    # Costes (calculados con LLMModelPricing en el momento de la llamada)
    input_cost_usd = db.Column(db.Float, nullable=True)
    output_cost_usd = db.Column(db.Float, nullable=True)
    total_cost_usd = db.Column(db.Float, nullable=True)

    # Rendimiento
    latency_ms = db.Column(db.Integer, nullable=True)

    # Estado
    status = db.Column(db.String(20), default='success')  # 'success', 'error', 'timeout'
    error_type = db.Column(db.String(100), nullable=True)

    # Hash del prompt para detectar duplicados y analizar variantes
    prompt_hash = db.Column(db.String(64), nullable=True)  # SHA-256

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index('idx_llm_usage_provider_model', 'provider', 'model', 'created_at'),
        Index('idx_llm_usage_service_type', 'service_type', 'created_at'),
        Index('idx_llm_usage_user', 'user_id', 'created_at'),
    )

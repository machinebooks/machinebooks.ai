# Extraído de: LibroTecnico/cap-05-diseno-base-datos.md
class LLMUsageLog(db.Model):
    """Registro de cada llamada a un modelo LLM.
    Cada invocación queda trazada con tokens, coste y latencia."""
    __tablename__ = 'llm_usage_logs'
    __bind_key__ = 'platform_core'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    # Nullable: algunas llamadas son de tareas de sistema, sin usuario
    service_type = db.Column(db.String(50), nullable=False)
    provider = db.Column(db.String(30), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)

    # Contadores de tokens según la respuesta de la API
    prompt_tokens = db.Column(db.Integer, default=0)
    completion_tokens = db.Column(db.Integer, default=0)
    total_tokens = db.Column(db.Integer, default=0)

    # Coste calculado al momento de la llamada con LLMModelPricing
    estimated_cost_eur = db.Column(db.Float, default=0.0)
    latency_ms = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), default='success')
    # Valores: success, error, timeout, rate_limited, fallback_used

    # Trazabilidad sin almacenar el prompt completo
    prompt_hash = db.Column(db.String(64))
    # SHA-256 del prompt: permite correlacionar sin almacenar contenido sensible

    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False, index=True)

    __table_args__ = (
        db.Index('idx_usage_user_date', 'user_id', 'created_at'),
        db.Index('idx_usage_service', 'service_type', 'created_at'),
        db.Index('idx_usage_provider_model', 'provider', 'model_name', 'created_at'),
    )

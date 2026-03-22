# Extraído de: LibroTecnico/cap-05-diseno-base-datos.md
class LLMServiceConfig(db.Model):
    """Configuración de servicio IA — qué modelo usar para cada tarea.
    Cambiar modelo sin redesplegar: solo actualizar esta tabla."""
    __tablename__ = 'llm_service_configs'
    __bind_key__ = 'platform_core'

    id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(50), unique=True, nullable=False)
    # Ejemplos: "chat", "document_analysis", "proposal_generation",
    #           "intent_classification", "cv_scoring", "opportunity_matching"
    provider = db.Column(db.String(30), nullable=False)
    # Valores: anthropic, openai, azure_openai, ollama, lm_studio
    model_name = db.Column(db.String(100), nullable=False)
    # Ejemplos: claude-sonnet-4-6, claude-haiku-4-5, gpt-4o, llama3.2
    temperature = db.Column(db.Float, default=0.7)
    max_tokens = db.Column(db.Integer, default=4096)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Fallback si el proveedor principal falla
    fallback_provider = db.Column(db.String(30), nullable=True)
    fallback_model = db.Column(db.String(100), nullable=True)

    # Integridad de configuración
    config_hash = db.Column(db.String(64))   # SHA-256 para detectar modificaciones directas
    last_verified_at = db.Column(db.DateTime)

    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(timezone.utc))

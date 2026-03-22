# Extraído de: LibroTecnico/cap-22-observabilidad.md
class FeatureUsageEvent(db.Model):
    """Evento granular de uso de funcionalidades.

    Permite análisis de funnel: started → completed (éxito)
                                         → abandoned (abandono)
    El campo session_id agrupa los eventos de una misma sesión de trabajo.
    """
    __tablename__ = 'feature_usage_events'
    __bind_key__ = 'platform_core'

    id = db.Column(db.Integer, primary_key=True)

    # Usuario y sesión
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=True)  # Agrupa eventos relacionados

    # Funcionalidad
    feature_name = db.Column(db.String(100), nullable=False)
    # Ejemplos: 'document_analyzer', 'proposal_generator', 'cv_analyzer',
    #           'analytics_chat', 'opportunity_search', 'proactive_alert'

    action = db.Column(db.String(50), nullable=False)
    # Valores: 'started', 'completed', 'abandoned', 'error', 'feedback_given'

    # Contexto enriquecido (diferente según la funcionalidad)
    context = db.Column(db.JSON, nullable=True)
    # Ejemplos:
    # document_analyzer: {"document_type": "requisitos", "pages": 182, "step": 2}
    # analytics_chat: {"query_type": "trend", "time_range": "90d"}
    # proposal_generator: {"proposal_type": "competitiva", "ai_sections": 4}

    # Timing
    duration_seconds = db.Column(db.Float, nullable=True)  # Solo en 'completed'

    # Calidad (si el usuario la proporciona)
    user_rating = db.Column(db.Integer, nullable=True)  # 1-5

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index('idx_feature_usage_feature_action', 'feature_name', 'action'),
        Index('idx_feature_usage_user_session', 'user_id', 'session_id'),
        Index('idx_feature_usage_created', 'created_at'),
    )

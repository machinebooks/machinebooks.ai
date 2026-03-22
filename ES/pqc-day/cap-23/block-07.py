# Extraído de: LibroPQC/cap-23-observabilidad.md
class AIUsageLog(db.Model):
    """Registro detallado de uso de IA.
    Combina audit trail con tracking de costes y rendimiento."""
    __tablename__ = 'ai_usage_logs'

    id = db.Column(db.Integer, primary_key=True)
    # Relaciones: qué servicio, qué proveedor, qué usuario
    service_id = db.Column(
        db.Integer, db.ForeignKey('ai_services.id'), nullable=True
    )
    provider_id = db.Column(
        db.Integer, db.ForeignKey('ai_providers.id'), nullable=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=True
    )
    # Modelo utilizado (claude-sonnet-4-6, etc.)
    model = db.Column(db.String(200))
    # Tipo de operación
    operation = db.Column(db.String(100))  # 'chat', 'pqc_analysis'

    # Métricas de consumo
    tokens_in = db.Column(db.Integer, default=0)
    tokens_out = db.Column(db.Integer, default=0)
    tokens_total = db.Column(db.Integer, default=0)
    cost_usd = db.Column(db.Float, default=0.0)
    latency_ms = db.Column(db.Integer)

    # Estado de la operación
    status = db.Column(
        db.Enum('success', 'error', 'timeout'),
        default='success'
    )
    error_message = db.Column(db.Text)

    # Trazabilidad sin exponer contenido sensible
    request_hash = db.Column(db.String(64))  # SHA-256 del prompt
    client_id = db.Column(
        db.Integer, db.ForeignKey('clients.id'), nullable=True
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Extraído de: LibroPQC/cap-14-gobernanza-ia.md
class AIUsageLog(db.Model):
    """Log detallado de cada llamada a IA — audit trail + tracking de costes.
    No almacena contenido sensible; solo metadatos de la operación."""
    __tablename__ = 'ai_usage_logs'

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('ai_services.id'))
    provider_id = db.Column(db.Integer, db.ForeignKey('ai_providers.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    model = db.Column(db.String(200))
    operation = db.Column(db.String(100))        # 'chat', 'pqc_analysis', etc.
    tokens_in = db.Column(db.Integer, default=0)
    tokens_out = db.Column(db.Integer, default=0)
    tokens_total = db.Column(db.Integer, default=0)
    cost_usd = db.Column(db.Float, default=0.0)
    latency_ms = db.Column(db.Integer)
    status = db.Column(db.Enum('success', 'error', 'timeout'), default='success')
    error_message = db.Column(db.Text)
    request_hash = db.Column(db.String(64))      # SHA-256 del prompt, para deduplicación
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

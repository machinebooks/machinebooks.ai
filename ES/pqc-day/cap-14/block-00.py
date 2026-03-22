# Extraído de: LibroPQC/cap-14-gobernanza-ia.md
from app.extensions import db
from datetime import datetime

class AIProvider(db.Model):
    """Registro de proveedores LLM — reemplaza la configuración
    por variables de entorno con un registro auditable."""
    __tablename__ = 'ai_providers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    provider_type = db.Column(
        db.Enum('openai', 'azure_openai', 'anthropic', 'ollama',
                'lmstudio', 'azure_ai_foundry', 'groq', 'custom'),
        nullable=False
    )
    endpoint = db.Column(db.String(500))
    api_key_encrypted = db.Column(db.Text)       # cifrado a nivel de aplicación
    default_model = db.Column(db.String(200))
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    # Métricas agregadas — actualizadas por cada escritura en usage_log
    total_tokens_used = db.Column(db.BigInteger, default=0)
    total_cost_usd = db.Column(db.Float, default=0.0)
    cost_per_1k_tokens_in = db.Column(db.Float, default=0.0)
    cost_per_1k_tokens_out = db.Column(db.Float, default=0.0)

    # Estado del último test de conectividad
    last_test_status = db.Column(
        db.Enum('success', 'failure', 'not_tested'),
        default='not_tested'
    )
    last_test_latency_ms = db.Column(db.Integer)

    # Relaciones
    services = db.relationship('AIService', backref='provider', lazy='dynamic')
    usage_logs = db.relationship('AIUsageLog', backref='provider', lazy='dynamic')

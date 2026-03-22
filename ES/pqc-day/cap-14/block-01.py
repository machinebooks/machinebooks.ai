# Extraído de: LibroPQC/cap-14-gobernanza-ia.md
class AIService(db.Model):
    """Servicio IA configurable — temperatura, modelo y prompts
    por caso de uso, sin hardcodear en código."""
    __tablename__ = 'ai_services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), default='General')
    provider_id = db.Column(db.Integer, db.ForeignKey('ai_providers.id'))
    model = db.Column(db.String(200))
    temperature = db.Column(db.Float, default=0.7)
    max_tokens = db.Column(db.Integer, default=4096)
    timeout_seconds = db.Column(db.Integer, default=120)
    is_active = db.Column(db.Boolean, default=True)

    # Campos de validación del marco de compliance IA
    risk_level = db.Column(db.Enum('low', 'medium', 'high'), default='low')
    validation_status = db.Column(
        db.Enum('pending', 'approved', 'approved_with_conditions', 'rejected'),
        default='pending'
    )
    approved_at = db.Column(db.DateTime)
    next_review_at = db.Column(db.DateTime)
    uses_personal_data = db.Column(db.Boolean, default=False)
    training_data_use_disabled = db.Column(db.Boolean, default=True)

    prompts = db.relationship('AIPrompt', backref='service', lazy='dynamic',
                               cascade='all, delete-orphan')

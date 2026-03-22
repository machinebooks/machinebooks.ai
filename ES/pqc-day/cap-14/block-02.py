# Extraído de: LibroPQC/cap-14-gobernanza-ia.md
class AIPrompt(db.Model):
    """Prompt versionado — ningún prompt hardcodeado en código."""
    __tablename__ = 'ai_prompts'

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('ai_services.id'),
                           nullable=False)
    role = db.Column(db.Enum('system', 'user', 'assistant'), default='system')
    name = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), default='es')
    version = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

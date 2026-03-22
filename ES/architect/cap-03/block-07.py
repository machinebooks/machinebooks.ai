# Extraído de: LibroTecnico/cap-03-ecosistema-claude.md
# Modelo de equipo: la sesión que agrupa a los agentes
# Fichero: backend/models/agent_team.py

class AgentTeam(db.Model):
    """Equipo de agentes IA colaborando en una tarea compleja."""
    __tablename__ = 'agent_teams'

    id = db.Column(db.Integer, primary_key=True)
    team_uuid = db.Column(db.String(36), unique=True, nullable=False,
                          default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    user_id = db.Column(db.Integer, nullable=False, index=True)
    project_id = db.Column(db.Integer, nullable=True, index=True)
    lead_agent_slug = db.Column(db.String(50), nullable=False)
    team_template = db.Column(db.String(50), nullable=True)  # "full_bid_preparation"
    progress = db.Column(db.Integer, default=0)
    final_summary = db.Column(db.Text, nullable=True)

    # Relaciones: tareas y mensajes del equipo
    tasks = db.relationship('TeamTask', backref='team', lazy='dynamic',
                            order_by='TeamTask.sort_order')
    messages = db.relationship('AgentMessage', backref='team', lazy='dynamic',
                               order_by='AgentMessage.created_at')

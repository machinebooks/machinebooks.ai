# Extraído de: LibroTecnico/cap-03-ecosistema-claude.md
class AgentMessage(db.Model):
    """Mensaje de comunicación entre agentes dentro de un equipo."""
    __tablename__ = 'agent_messages'

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('agent_teams.id'),
                        nullable=False, index=True)
    from_agent = db.Column(db.String(50), nullable=False)   # slug, "lead" o "user"
    to_agent = db.Column(db.String(50), nullable=False)      # slug, "lead" o "all"
    message_type = db.Column(db.String(30), nullable=False)  # task_result, feedback...
    content = db.Column(db.Text, nullable=True)
    metadata_json = db.Column(db.JSON, nullable=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False)

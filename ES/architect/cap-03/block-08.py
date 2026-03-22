# Extraído de: LibroTecnico/cap-03-ecosistema-claude.md
class TeamTask(db.Model):
    """Tarea individual asignada a un agente dentro del equipo."""
    __tablename__ = 'team_tasks'

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('agent_teams.id'),
                        nullable=False, index=True)
    title = db.Column(db.String(300), nullable=False)
    task_type = db.Column(db.String(50), nullable=False)
    assigned_agent_slug = db.Column(db.String(50), nullable=False)

    # Dependencias: lista de task_uuids de los que depende esta tarea
    depends_on = db.Column(db.JSON, nullable=True)

    status = db.Column(db.String(20), nullable=False, default='pending')
    input_data = db.Column(db.JSON, nullable=True)
    output_data = db.Column(db.JSON, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, default=0)

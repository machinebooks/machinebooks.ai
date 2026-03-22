# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
class AgentToolAssignment(db.Model):
    """Asignación M2M de herramientas a agentes con orden y config."""
    __tablename__ = 'agent_tool_assignments'

    agent_definition_id = db.Column(db.Integer, db.ForeignKey('agent_definitions.id'))
    tool_name = db.Column(db.String(100))       # Nombre en el Tool Registry
    is_enabled = db.Column(db.Boolean, default=True)
    tool_config = db.Column(db.JSON)            # Config específica para este agente
    sort_order = db.Column(db.Integer, default=0)

class AgentGuardrailConfig(db.Model):
    """Configuración de guardrails individual por agente."""
    __tablename__ = 'agent_guardrail_configs'

    agent_definition_id = db.Column(db.Integer, db.ForeignKey('agent_definitions.id'))
    guardrail_type = db.Column(db.String(50))   # 8 tipos disponibles
    is_enabled = db.Column(db.Boolean, default=True)
    severity = db.Column(db.String(20), default='block')  # block | warn
    config = db.Column(db.JSON)                 # Params específicos

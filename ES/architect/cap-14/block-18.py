# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
class AgentDefinition(db.Model):
    __tablename__ = 'agent_definitions'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(20), default='draft', index=True)  # draft|active|archived
    agent_type = db.Column(db.String(30), default='assistant')       # 4 tipos posibles
    execution_mode = db.Column(db.String(30), default='chat_rag')    # 3 modos

    # Configuración del modelo
    llm_service_type = db.Column(db.String(50), default='chat')
    temperature = db.Column(db.Float, default=1.0)
    max_tokens = db.Column(db.Integer, default=2000)
    max_iterations = db.Column(db.Integer, default=20)
    timeout_seconds = db.Column(db.Integer, default=120)

    # Prompt y enrutamiento
    system_prompt = db.Column(db.Text)
    prompt_key = db.Column(db.String(100))        # Ref. a prompts centralizados
    intent_keywords = db.Column(db.JSON)           # Para auto-routing
    reasoning_effort = db.Column(db.String(10), default='medium')

    # Relaciones M2M
    tools = db.relationship('AgentToolAssignment', cascade='all, delete-orphan')
    guardrails = db.relationship('AgentGuardrailConfig', cascade='all, delete-orphan')

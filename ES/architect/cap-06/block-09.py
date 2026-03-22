# Extraído de: LibroTecnico/cap-06-iam-seguridad.md
class GuardrailType:
    """Catálogo de guardrails disponibles para agentes.
    Cada agente puede activar/desactivar cualquier combinación."""
    PROMPT_INJECTION = 'prompt_injection'      # Detección de inyección de prompts
    PII_DETECTION = 'pii_detection'            # Detección de PII en entrada
    PII_REDACTION = 'pii_redaction'            # Redacción de PII en salida
    OFF_TOPIC = 'off_topic'                    # Filtro de temas fuera de alcance
    MALICIOUS_CONTENT = 'malicious_content'    # Contenido peligroso (SQL injection, etc.)
    OUTPUT_LENGTH = 'output_length'            # Límite de longitud de respuesta
    FORBIDDEN_PATTERNS = 'forbidden_patterns'  # Patrones prohibidos configurables
    HALLUCINATION_CHECK = 'hallucination_check'  # Detección de alucinaciones

class AgentGuardrailConfig(db.Model):
    """Configuración de guardrail por agente — granularidad individual."""
    __tablename__ = 'agent_guardrail_configs'

    id = db.Column(db.Integer, primary_key=True)
    agent_definition_id = db.Column(
        db.Integer, db.ForeignKey('agent_definitions.id', ondelete='CASCADE'),
        nullable=False, index=True,
    )
    guardrail_type = db.Column(db.String(50), nullable=False)
    is_enabled = db.Column(db.Boolean, default=True)
    severity = db.Column(db.String(20), default='block')  # allow, sanitize, block
    config = db.Column(db.JSON, nullable=True)  # Parámetros específicos del guardrail

    __table_args__ = (
        db.UniqueConstraint('agent_definition_id', 'guardrail_type',
                            name='uq_agent_guardrail'),
    )

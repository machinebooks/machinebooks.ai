# Extraído de: LibroFinOps/cap-21-aiact-auditoria.md
# models/llm_audit.py (continuación)
class LLMAIIncident(Base):
    """
    Registro de incidentes del sistema de IA.
    Obligatorio para sistemas de riesgo medio y alto (AI Act).
    """
    __tablename__ = "llm_ai_incident"

    id = Column(Integer, primary_key=True)
    usage_log_id = Column(Integer, ForeignKey("llm_usage_log.id"))
    severity = Column(String(20), nullable=False)   # low | medium | high | critical
    incident_type = Column(String(100))   # factual_error | harmful_content | etc.
    description = Column(Text, nullable=False)
    detected_by = Column(String(50))      # user | automatic | reviewer
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    resolution = Column(Text)
    corrective_action = Column(Text)
    reported_to_authority = Column(Boolean, default=False)
    root_cause = Column(Text)
    affected_users_count = Column(Integer, default=1)

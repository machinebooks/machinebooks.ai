# Extraído de: LibroCISO/cap-14-gobernanza-ia-ai-act.md
# Ejemplo didáctico: modelos/ai_governance_controls.py
# Controles de gobernanza y registro de incidentes de IA

class AIGovernanceControl(BaseModel):
    """Control de gobernanza aplicado a un sistema de IA.

    Cada control es una medida técnica u organizativa que la organización
    aplica para mitigar un riesgo identificado en el sistema de IA.
    Mapea directamente a los requisitos Art. 9-15 y a controles ISO 42001.
    """
    __tablename__ = "ai_governance_controls"

    ai_record_id = Column(ForeignKey("ai_governance_records.id"), nullable=False)
    control_name = Column(String(200), nullable=False)
    control_description = Column(Text, nullable=False)
    control_type = Column(String(50))          # technical, organizational, procedural
    ai_act_article = Column(String(20))        # Art. 9, Art. 10, etc.
    iso42001_control = Column(String(20))      # A.6.2.3, A.6.2.6, etc.

    # Estado
    implementation_status = Column(String(50)) # planned, implemented, verified, failed
    evidence_reference = Column(Text)          # Referencia a evidencia en el GRC
    last_verified = Column(DateTime)           # Última verificación
    next_review = Column(DateTime)             # Próxima revisión programada

    ai_record = relationship("AIGovernanceRecord", back_populates="governance_controls")


class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AIGovernanceIncident(BaseModel):
    """Incidente de gobernanza de IA.

    Registra eventos adversos: decisiones erróneas del sistema, sesgos detectados
    en producción, fallos de supervisión humana, brechas de datos en el pipeline
    de IA, o cualquier situación que requiera investigación y corrección.

    Para GPAI con riesgo sistémico, los incidentes graves deben notificarse
    a la Oficina Europea de IA (Art. 62).
    """
    __tablename__ = "ai_governance_incidents"

    ai_record_id = Column(ForeignKey("ai_governance_records.id"), nullable=False)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(SQLEnum(IncidentSeverity), nullable=False)

    # Clasificación del incidente
    incident_type = Column(String(100))        # bias_detected, accuracy_degradation,
                                                # privacy_breach, safety_issue,
                                                # unauthorized_output, system_failure
    affected_persons_count = Column(Float)      # Número estimado de personas afectadas

    # Gestión
    reported_by = Column(ForeignKey("users.id"))
    reported_date = Column(DateTime, nullable=False)
    investigation_status = Column(String(50))  # open, investigating, resolved, closed
    root_cause = Column(Text)
    corrective_actions = Column(Text)
    resolution_date = Column(DateTime)

    # Notificación regulatoria
    requires_notification = Column(String(10), default="no")  # yes, no, pending
    notification_authority = Column(String(200))               # AEPD, Oficina Europea IA, etc.
    notification_date = Column(DateTime)
    notification_reference = Column(String(200))               # Número de expediente

    ai_record = relationship("AIGovernanceRecord", back_populates="governance_incidents")

# Extraído de: LibroCISO/cap-14-gobernanza-ia-ai-act.md
# Ejemplo didáctico: modelos/conformity_assessment.py
# Evaluación de conformidad según AI Act Art. 9-15

class CheckpointStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    CONDITIONAL = "conditional"  # Cumple con condiciones documentadas


class ConformityCheckpoint(str, Enum):
    """Los 7 requisitos de conformidad del AI Act para alto riesgo."""
    RISK_MANAGEMENT = "risk_management"        # Art. 9 — Gestión de riesgos
    DATA_GOVERNANCE = "data_governance"         # Art. 10 — Gobernanza de datos
    TECHNICAL_DOCS = "technical_documentation"  # Art. 11 — Documentación técnica
    RECORD_KEEPING = "record_keeping"           # Art. 12 — Registro de actividad
    TRANSPARENCY = "transparency"              # Art. 13 — Transparencia
    HUMAN_OVERSIGHT = "human_oversight"         # Art. 14 — Supervisión humana
    ACCURACY_ROBUSTNESS = "accuracy_robustness" # Art. 15 — Precisión y robustez


# Pesos para scoring de conformidad (suman 1.0)
CHECKPOINT_WEIGHTS = {
    ConformityCheckpoint.RISK_MANAGEMENT: 0.20,      # Mayor peso: base de todo
    ConformityCheckpoint.DATA_GOVERNANCE: 0.15,
    ConformityCheckpoint.TECHNICAL_DOCS: 0.10,
    ConformityCheckpoint.RECORD_KEEPING: 0.10,
    ConformityCheckpoint.TRANSPARENCY: 0.10,
    ConformityCheckpoint.HUMAN_OVERSIGHT: 0.20,       # Mayor peso: exigencia clave
    ConformityCheckpoint.ACCURACY_ROBUSTNESS: 0.15,
}


class ConformityAssessment(BaseModel):
    """Evaluación de conformidad de un sistema de IA de alto riesgo."""
    __tablename__ = "ai_conformity_assessments"

    ai_record_id = Column(ForeignKey("ai_governance_records.id"), nullable=False)
    checkpoint = Column(SQLEnum(ConformityCheckpoint), nullable=False)
    status = Column(SQLEnum(CheckpointStatus), default=CheckpointStatus.NOT_STARTED)

    # Evaluación
    evaluator_id = Column(ForeignKey("users.id"))          # Quién evalúa
    evaluation_date = Column(DateTime)                      # Cuándo
    findings = Column(Text)                                 # Hallazgos
    conditions = Column(Text)                               # Condiciones si status=conditional
    evidence_references = Column(JSON)                      # Referencias a documentos/pruebas

    # Mapeo ISO 42001
    iso42001_controls = Column(JSON)                        # Controles ISO 42001 mapeados

    # Relación
    ai_record = relationship("AIGovernanceRecord", back_populates="conformity_assessments")

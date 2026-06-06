# Extraído de: LibroAIGateway/cap-23-compliance-regulatorio.md
# gateway/app/models/ai_use_case.py
class AIUseCase(Base):
    """Registro de caso de uso IA con clasificación AI Act."""
    __tablename__ = "ai_use_cases"

    id                      = Column(Integer, primary_key=True)
    name                    = Column(String(255), nullable=False)   # Nombre interno
    description             = Column(Text)                          # Descripción funcional
    ai_act_risk_level       = Column(String(30), default="unclassified")  # high_risk, ...
    human_oversight_required = Column(Boolean, default=False)       # Supervisión obligatoria
    transparency_required   = Column(Boolean, default=False)        # Aviso de IA al usuario
    assessment_status       = Column(String(30))                    # Estado de la evaluación
    technical_file_status   = Column(String(30))                    # Estado del expediente técnico
    assessment_json         = Column(JSON)                          # Evaluación de impacto
    is_active               = Column(Boolean, default=True)
    organization_id         = Column(Integer, ForeignKey("organizations.id"))

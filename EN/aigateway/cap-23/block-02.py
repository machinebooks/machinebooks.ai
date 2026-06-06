# Extracted from: LibroAIGateway/cap-23-compliance-regulatory.md
# gateway/app/models/ai_use_case.py
class AIUseCase(Base):
    """AI use case registry with AI Act classification."""
    __tablename__ = "ai_use_cases"

    id                       = Column(Integer, primary_key=True)
    name                     = Column(String(255), nullable=False)  # Internal name
    description              = Column(Text)                         # Functional description
    ai_act_risk_level        = Column(String(30), default="unclassified")  # high_risk, ...
    human_oversight_required = Column(Boolean, default=False)       # Mandatory oversight
    transparency_required    = Column(Boolean, default=False)       # AI notice to the user
    assessment_status        = Column(String(30))                  # Assessment status
    technical_file_status    = Column(String(30))                  # Technical file status
    assessment_json          = Column(JSON)                        # Impact assessment
    is_active                = Column(Boolean, default=True)
    organization_id          = Column(Integer, ForeignKey("organizations.id"))

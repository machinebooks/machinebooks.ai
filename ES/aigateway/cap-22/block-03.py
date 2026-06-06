# Extraído de: LibroAIGateway/cap-22-governance-engine.md
class GovernanceCheck(Base):
    __tablename__ = "governance_checks"

    check_key = Column(String(100), unique=True, nullable=False)
    control_code = Column(String(20), nullable=True)
    category = Column(String(50), nullable=False)
    check_type = Column(String(20), default="service")  # service|static|manual
    severity = Column(String(20), default="medium")     # low|medium|high|critical
    frequency_days = Column(Integer, default=30, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)

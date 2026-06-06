# Extraído de: LibroAIGateway/cap-22-governance-engine.md
class GovernanceCheckRun(Base):
    __tablename__ = "governance_check_runs"

    check_id = Column(Integer, ForeignKey("governance_checks.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    status = Column(String(20), nullable=False)  # pass|fail|warn|manual|error
    summary = Column(String(500), nullable=False)
    details = Column(JSON, nullable=True)
    evidence = Column(JSON, nullable=True)
    duration_ms = Column(Integer, nullable=True)

# Extracted from: LibroAIGateway/cap-22-governance-engine.md
class GovernanceControl(Base):
    __tablename__ = "governance_controls"

    section = Column(String(20), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    title = Column(String(300), nullable=False)
    status = Column(String(20), default="pending")  # cumple|no_cumple|parcial|n_a|pending
    evidence = Column(Text, nullable=True)
    priority = Column(String(10), default="medium")  # low|medium|high|critical

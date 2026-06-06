# Extraído de: LibroAIGateway/cap-22-governance-engine.md
class GovernanceIncident(Base):
    __tablename__ = "governance_incidents"

    severity = Column(String(20), default="medium")  # low|medium|high|critical
    status = Column(String(20), default="open")       # open|investigating|resolved|closed
    remediation = Column(Text, nullable=True)
    affected_service = Column(String(100), nullable=True)

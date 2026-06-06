# Extraído de: LibroAIGateway/cap-22-governance-engine.md
class GovernanceReview(Base):
    __tablename__ = "governance_reviews"

    status = Column(String(20), default="scheduled")  # scheduled|in_progress|completed
    findings = Column(Text, nullable=True)
    next_review_date = Column(DateTime, nullable=True)

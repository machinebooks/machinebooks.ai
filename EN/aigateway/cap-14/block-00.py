# Extracted from: LibroAIGateway/cap-14-pricing-cost-roi.md
class LLMPricing(Base):
    __tablename__ = "llm_pricing"
    __table_args__ = (
        UniqueConstraint("organization_id", "model", name="uq_llm_pricing_org_model"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    model = Column(String(100), nullable=False)
    provider = Column(String(20), nullable=False)
    prompt_usd_per_1k = Column(DECIMAL(10, 8), nullable=False)
    cached_input_usd_per_1k = Column(DECIMAL(10, 8), nullable=True)
    output_usd_per_1k = Column(DECIMAL(10, 8), nullable=False)
    reasoning_output_usd_per_1k = Column(DECIMAL(10, 8), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

# Extraído de: LibroAIGateway/cap-14-pricing-cost-roi.md
class CostAllocation(Base):
    __tablename__ = "cost_allocations"

    monthly_budget_usd = Column(DECIMAL(10, 2), nullable=False, default=0)
    alert_threshold_pct = Column(SmallInteger, nullable=False, default=80)

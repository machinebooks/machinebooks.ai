# Extracted from: LibroAIGateway/cap-02-mental-model-tenancy.md
class TeamModelQuota(Base):
    __tablename__ = "team_model_quotas"

    team_id = Column(ForeignKey("teams.id"), nullable=False)
    bucket = Column(String(30))           # session_5h | daily | weekly | monthly
    entitlement = Column(Numeric(10, 3))  # -1 = unlimited
    used = Column(Numeric(10, 3), default=0)
    overage_permitted = Column(Boolean, default=False)

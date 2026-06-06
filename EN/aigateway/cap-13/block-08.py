# Extracted from: LibroAIGateway/cap-13-tenants-quotas.md
class UserModelQuota(Base):
    __tablename__ = "user_model_quotas"

    user_id           = Column(Integer, nullable=True)      # Preferred over device_id
    device_id         = Column(String(64), nullable=True)   # Fallback without user
    organization_id   = Column(Integer, nullable=True)      # Cross-tenant isolation
    bucket            = Column(String(30), nullable=False)  # session_5h | daily | ...
    entitlement       = Column(Numeric(10, 3))              # Budget (EUR). -1 = unlimited
    used              = Column(Numeric(10, 3), default=0)   # Accumulated consumption
    overage_count     = Column(Integer, default=0)          # Overage counter
    overage_permitted = Column(Boolean, default=False)      # Allows overage
    period_start      = Column(DateTime, nullable=False)    # Window start
    period_end        = Column(DateTime, nullable=False)    # Window end

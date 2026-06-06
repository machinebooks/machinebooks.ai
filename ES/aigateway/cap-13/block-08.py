# Extraído de: LibroAIGateway/cap-13-tenants-cuotas.md
class UserModelQuota(Base):
    __tablename__ = "user_model_quotas"

    user_id           = Column(Integer, nullable=True)      # Preferible a device_id
    device_id         = Column(String(64), nullable=True)   # Fallback sin user
    organization_id   = Column(Integer, nullable=True)      # Aislamiento cross-tenant
    bucket            = Column(String(30), nullable=False)  # session_5h | daily | ...
    entitlement       = Column(Numeric(10, 3))              # Presupuesto (EUR). -1 = ilimitado
    used              = Column(Numeric(10, 3), default=0)   # Consumo acumulado
    overage_count     = Column(Integer, default=0)          # Contador de sobregiro
    overage_permitted = Column(Boolean, default=False)      # Permite sobregiro
    period_start      = Column(DateTime, nullable=False)    # Inicio de ventana
    period_end        = Column(DateTime, nullable=False)    # Fin de ventana

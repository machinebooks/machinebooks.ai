# Extraído de: LibroAIGateway/cap-02-modelo-mental-tenancy.md
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    slug = Column(String(100), unique=True, index=True)
    sso_enabled = Column(Boolean, default=False)
    sso_config = Column(JSON, nullable=True)
    white_label = Column(JSON, nullable=True)
    features = Column(JSON, nullable=True)
    data_residency = Column(String(50), nullable=True)
    allowed_providers = Column(JSON, nullable=True)
    blocked_regions = Column(JSON, nullable=True)
    max_devices = Column(Integer, nullable=True)
    alert_threshold_pct = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)

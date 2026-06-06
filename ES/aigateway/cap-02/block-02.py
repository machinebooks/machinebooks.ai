# Extraído de: LibroAIGateway/cap-02-modelo-mental-tenancy.md
class Team(Base):
    __tablename__ = "teams"

    parent_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True)
    preferred_model_key = Column(String(100), nullable=True)
    monthly_budget_eur = Column(Numeric(10, 2), nullable=True)
    budget_pooled = Column(Boolean, default=True)
    max_devices_per_user = Column(Integer, nullable=True)

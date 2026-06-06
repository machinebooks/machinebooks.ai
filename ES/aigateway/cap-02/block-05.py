# Extraído de: LibroAIGateway/cap-02-modelo-mental-tenancy.md
class Application(Base):
    __tablename__ = "applications"

    slug = Column(String(64), unique=True, index=True)
    owner_team_id = Column(ForeignKey("teams.id", ondelete="RESTRICT"))
    key_hash = Column(String(64), unique=True)
    allowed_purposes = Column(JSON, default=list)
    model_whitelist = Column(JSON, nullable=True)
    monthly_budget_eur = Column(Numeric(10, 2), nullable=True)
    status = Column(Enum("active", "suspended", "revoked"), default="active")

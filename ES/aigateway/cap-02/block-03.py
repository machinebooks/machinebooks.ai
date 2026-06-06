# Extraído de: LibroAIGateway/cap-02-modelo-mental-tenancy.md
class User(Base):
    __tablename__ = "users"

    organization_id = Column(ForeignKey("organizations.id"), index=True)
    team_id = Column(ForeignKey("teams.id", ondelete="SET NULL"), index=True)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(Enum("admin", "manager", "viewer", "compliance_champion"))
    preferred_model_key = Column(String(100), nullable=True)
    max_devices = Column(Integer, nullable=True)
    auth_source = Column(Enum("local", "sso"))
    mfa_enabled = Column(Boolean, default=False)

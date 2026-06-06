# Extraído de: LibroAIGateway/cap-02-modelo-mental-tenancy.md
class Device(Base):
    __tablename__ = "devices"

    device_id = Column(String(64), unique=True, nullable=False)   # SHA-256
    hostname = Column(String(255), nullable=True)
    linked_email = Column(String(255), nullable=True)
    app_type = Column(Enum("extension", "desktop", "service", "other"))
    is_active = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    user_id = Column(ForeignKey("users.id"), nullable=True)
    activation_code = Column(String(20), unique=True, nullable=True)

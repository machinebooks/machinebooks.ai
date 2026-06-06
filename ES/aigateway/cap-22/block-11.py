# Extraído de: LibroAIGateway/cap-22-governance-engine.md
class PermissionRule(Base):
    __tablename__ = "permission_rules"

    scope_type = Column(Enum("role", "user", "device", "team", "all"))
    scope_value = Column(String(100))     # "admin", user_id, device_id, team
    tool_name = Column(String(100), nullable=False)
    tool_pattern = Column(String(200))     # "rm*" para bash, "*.py" para files
    behavior = Column(Enum("allow", "deny", "ask"))
    priority = Column(Integer, default=0)

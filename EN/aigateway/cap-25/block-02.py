# Extracted from: LibroAIGateway/cap-25-mcp-registration-catalog.md
class McpServerAssignment(Base):
    __tablename__ = "mcp_server_assignments"

    mcp_id = Column(Integer, ForeignKey("mcp_servers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    role = Column(String(50), nullable=True)

    __table_args__ = (
        UniqueConstraint("mcp_id", "user_id", "role"),
    )

# Extracted from: LibroAIGateway/cap-25-mcp-registration-catalog.md
class McpServer(Base):
    __tablename__ = "mcp_servers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(MysqlInt(unsigned=True), ForeignKey("organizations.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    slug = Column(String(100), nullable=False)
    name = Column(String(150), nullable=False)
    transport = Column(Enum("stdio", "sse", "http"), nullable=False)
    command = Column(String(500), nullable=True)      # stdio: binary to execute
    args = Column(JSON, nullable=True)                # stdio: arguments
    env = Column(JSON, nullable=True)                 # stdio: environment variables
    url = Column(String(500), nullable=True)          # sse/http: endpoint
    headers = Column(JSON, nullable=True)             # sse/http: extra headers
    auth_type = Column(Enum("none", "bearer", "basic"), nullable=False, default="none")
    auth_secret_ref = Column(String(150), nullable=True)  # ref to vault/DB
    scope = Column(Enum("user", "org", "global"), nullable=False, default="user")
    is_enabled = Column(Boolean, nullable=False, default=True)

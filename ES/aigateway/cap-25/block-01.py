# Extraído de: LibroAIGateway/cap-25-mcp-registro-catalogo.md
class McpServer(Base):
    __tablename__ = "mcp_servers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(MysqlInt(unsigned=True), ForeignKey("organizations.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    slug = Column(String(100), nullable=False)
    name = Column(String(150), nullable=False)
    transport = Column(Enum("stdio", "sse", "http"), nullable=False)
    command = Column(String(500), nullable=True)      # stdio: binario a ejecutar
    args = Column(JSON, nullable=True)                # stdio: argumentos
    env = Column(JSON, nullable=True)                 # stdio: variables de entorno
    url = Column(String(500), nullable=True)          # sse/http: endpoint
    headers = Column(JSON, nullable=True)             # sse/http: headers extra
    auth_type = Column(Enum("none", "bearer", "basic"), nullable=False, default="none")
    auth_secret_ref = Column(String(150), nullable=True)  # ref a vault/BD
    scope = Column(Enum("user", "org", "global"), nullable=False, default="user")
    is_enabled = Column(Boolean, nullable=False, default=True)

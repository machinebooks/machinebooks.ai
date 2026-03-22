# Extraído de: LibroUsuario/cap-10-construir-tu-conector-mcp.md
servidor = FastMCP("gestion-empresa")
API_BASE = "https://api.ejemplo.com/v1"
API_TOKEN = os.environ.get("API_TOKEN", "tu-token-aqui")

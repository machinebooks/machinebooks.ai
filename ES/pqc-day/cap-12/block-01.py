# Extraído de: LibroPQC/cap-12-agente-autonomo.md
class RepositoryTools:
    """Herramientas de exploración de repositorios para el agente."""

    IGNORE_DIRS = {
        '__pycache__', 'node_modules', '.git', '.svn', 'venv',
        '.venv', 'dist', 'build', '.idea', 'coverage', '.eggs'
    }

    def __init__(self, repo_path: str, max_file_size: int = 100_000):
        self.repo_path = Path(repo_path)
        self.max_file_size = max_file_size  # 100 KB por defecto

    def get_tool_definitions(self) -> list:
        """Devuelve las 5 herramientas en formato OpenAI function calling."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "Lista archivos y carpetas en un directorio.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "recursive": {"type": "boolean"}
                        }
                    }
                }
            },
            # read_file, search_code, find_crypto_usage, get_file_summary
            # (misma estructura con parámetros específicos)
        ]

    def execute_tool(self, tool_name: str, arguments: dict) -> dict:
        """Despacho central: nombre → método Python."""
        handlers = {
            "list_files":        self._list_files,
            "read_file":         self._read_file,
            "search_code":       self._search_code,
            "find_crypto_usage": self._find_crypto_usage,
            "get_file_summary":  self._get_file_summary,
        }
        handler = handlers.get(tool_name)
        if not handler:
            return {'success': False, 'error': f'Herramienta desconocida: {tool_name}'}
        return handler(**arguments)

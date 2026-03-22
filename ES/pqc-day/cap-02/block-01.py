# Extraído de: LibroPQC/cap-02-arquitecto-migracion.md
# Ejemplo didáctico: patrones/connectors/base.py
class BaseConnector:
    """Interfaz base para todos los conectores de repositorio y cloud."""

    def __init__(self, credentials: dict):
        self.credentials = credentials
        self._validate_credentials()

    def _validate_credentials(self):
        """Verifica que las credenciales necesarias están presentes."""
        raise NotImplementedError

    def test_connection(self) -> dict:
        """Prueba la conexión y devuelve estado + metadata."""
        raise NotImplementedError

    def list_repositories(self) -> list:
        """Lista repositorios accesibles con esta credencial."""
        raise NotImplementedError

    def get_file_content(self, repo: str, path: str, branch: str = "main") -> str:
        """Obtiene el contenido de un fichero específico."""
        raise NotImplementedError

    def list_files(self, repo: str, path: str = "", branch: str = "main") -> list:
        """Lista ficheros en un directorio del repositorio."""
        raise NotImplementedError

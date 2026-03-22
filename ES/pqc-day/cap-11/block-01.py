# Extraído de: LibroPQC/cap-11-analisis-semantico.md
class BaseAIProvider(ABC):
    """Clase base para todos los proveedores de IA"""

    def __init__(self, config: Dict, analysis_type: str = 'pqc'):
        self.config = config
        self.model = config.get('model')
        self.timeout = config.get('timeout', 120)
        self.analysis_type = analysis_type  # 'pqc' o 'owasp'

    @abstractmethod
    def analyze_code(self, code: str, filename: str,
                     context: Dict = None) -> Dict:
        """Analizar código — implementa cada proveedor"""
        pass

    @abstractmethod
    def test_connection(self) -> Dict:
        """Verificar que el proveedor está disponible"""
        pass

    def _build_pqc_prompt(self, code: str, filename: str,
                          language: str = None) -> str:
        """Prompt especializado en criptografía post-cuántica"""
        return f"""Eres un experto en criptografía post-cuántica (PQC).
Analiza el siguiente código buscando vulnerabilidades criptográficas
que serán explotables por computadoras cuánticas.

**ARCHIVO:** {filename}
**LENGUAJE:** {language or 'auto-detect'}

**CÓDIGO:**

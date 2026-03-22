# Extraído de: LibroPQC/cap-07-analisis-codigo.md
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class BaseConnector(ABC):
    """Clase base para todos los conectores de repositorio"""

    def __init__(self, config: Dict):
        self.config = config
        self.connection = None

    @abstractmethod
    def connect(self) -> bool:
        """Establecer conexión con el servicio"""
        pass

    @abstractmethod
    def test_connection(self) -> Dict:
        """Probar la conexión y devolver estado"""
        pass

    @abstractmethod
    def disconnect(self):
        """Cerrar conexión"""
        pass

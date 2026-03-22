# Extraído de: LibroConsultor/cap-04-rag-conocimiento.md
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from qdrant_client import QdrantClient, models
import voyageai
import anthropic

# Configuración
COLLECTION_NAME = "knowledge_base"
CHUNK_SIZE = 500       # tokens por fragmento
CHUNK_OVERLAP = 100    # tokens de solapamiento
EMBEDDING_MODEL = "voyage-3"

voyage = voyageai.Client(api_key="<TU_VOYAGE_KEY>")
qdrant = QdrantClient(host="localhost", port=6333)


@dataclass
class DocumentMetadata:
    """Metadatos estructurados de cada documento."""
    tipo: str              # propuesta, informe, metodologia, leccion
    sector: str            # publico, financiero, industrial, tecnologico
    year: int              # año del documento
    framework: str = ""    # ISO_27001, ENS, DORA, NIS2, AI_Act
    resultado: str = ""    # ganada, perdida, cancelada (solo propuestas)
    proyecto_id: str = ""  # identificador genérico del proyecto
    tags: list[str] = field(default_factory=list)

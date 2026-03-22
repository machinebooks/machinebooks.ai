# Extraído de: LibroConsultor/cap-17-memoria-institucional.md
# pipeline/ingest.py — Pipeline de ingesta de documentos
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import hashlib

@dataclass
class DocumentChunk:
    """Fragmento de documento listo para extracción."""
    doc_id: str
    chunk_index: int
    text: str
    source_file: str
    section_title: str  # Título de sección del documento original
    project_code: str
    author: str
    created_at: datetime

class DocumentIngester:
    """Ingesta documentos y produce chunks para extracción."""

    SUPPORTED_FORMATS = {".pdf", ".docx", ".pptx", ".md", ".eml"}
    MAX_CHUNK_WORDS = 800    # Fragmentos de ~800 palabras
    OVERLAP_WORDS = 100      # Solapamiento entre fragmentos

    def __init__(self, extractors: dict, queue):
        self.extractors = extractors  # {".pdf": PdfExtractor, ...}
        self.queue = queue            # Cola Celery para procesamiento async

    def ingest(self, file_path: Path, metadata: dict) -> list[DocumentChunk]:
        """Ingesta un documento y encola chunks para extracción."""
        # Verificar formato soportado
        if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Formato no soportado: {file_path.suffix}")

        # Verificar permisos de compartición
        sharing_level = metadata.get("sharing", "personal")
        if sharing_level == "personal":
            return []  # No se ingesta sin autorización

        # Extraer texto plano con secciones
        extractor = self.extractors[file_path.suffix.lower()]
        sections = extractor.extract_sections(file_path)

        # Generar ID único del documento
        doc_id = hashlib.sha256(
            f"{file_path.name}:{metadata['project']}:{metadata['author']}".encode()
        ).hexdigest()[:16]

        # Segmentar en chunks con solapamiento
        chunks = self._chunk_sections(sections, doc_id, metadata)

        # Encolar cada chunk para extracción + etiquetado
        for chunk in chunks:
            self.queue.send_task(
                "extraction.process_chunk",
                args=[chunk],
                queue="knowledge_extraction"
            )

        return chunks

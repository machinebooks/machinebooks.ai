# Extraído de: LibroTecnico/cap-12-rag-produccion.md
# Ejemplo didáctico: patrones/rag/document_processor.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader,
    UnstructuredPowerPointLoader,
)
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import pytesseract
from PIL import Image
import fitz  # PyMuPDF para detección de PDFs escaneados
import hashlib

class DocumentProcessor:
    """
    Pipeline completo de ingesta de documentos para RAG.
    Maneja PDF, DOCX, XLSX, PPTX con fallback a OCR para escaneados.
    """

    def __init__(self, qdrant_url: str, openai_api_key: str):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
            dimensions=3072,
            api_key=openai_api_key,
        )
        self.qdrant_client = QdrantClient(url=qdrant_url)
        # Chunking adaptativo: chunks de 800 tokens con 150 de solapamiento
        # El solapamiento evita que el contexto relevante quede partido entre chunks
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def compute_hash(self, file_path: str) -> str:
        """SHA-256 para detectar cambios y evitar reindexaciones innecesarias."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def is_scanned_pdf(self, file_path: str) -> bool:
        """
        Detecta si un PDF es principalmente imagen (escaneado).
        Heurístico: si menos del 10% de las páginas tienen texto seleccionable,
        se considera escaneado y se aplica OCR.
        """
        doc = fitz.open(file_path)
        pages_with_text = sum(
            1 for page in doc
            if len(page.get_text().strip()) > 50
        )
        return pages_with_text / max(len(doc), 1) < 0.1


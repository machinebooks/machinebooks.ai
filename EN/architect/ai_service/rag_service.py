"""
Chapter 12: RAG in production — Qdrant + LangChain + chunking strategies.

The Platform's RAG system:
  - 13 Qdrant collections, ~3.9M vectors
  - Embeddings: text-embedding-3-large (3072 dimensions)
  - 5 chunking strategies by document type
  - Hierarchical retrieval for technical proposals (Parent Document Retriever)
  - Access control per collection (Chapter 6)

Key insight: There is no universally optimal chunking strategy.
Document type matters as much as chunk size.
"""

import hashlib
import os
from typing import List, Optional

# In production: from langchain, qdrant_client, etc.
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import Qdrant
# from qdrant_client import QdrantClient


# =============================================================================
# Qdrant collections (Chapter 12)
# =============================================================================

COLLECTIONS = {
    "operations_general":    {"dims": 3072, "distance": "Cosine"},
    "proposals_technical":   {"dims": 3072, "distance": "Cosine"},
    "cv_profiles":           {"dims": 3072, "distance": "Cosine"},
    "opportunities":         {"dims": 3072, "distance": "Cosine"},
    "commercial_catalog":    {"dims": 3072, "distance": "Cosine"},   # Restricted
    "regulatory_corpus":     {"dims": 3072, "distance": "Cosine"},
    "project_history":       {"dims": 3072, "distance": "Cosine"},   # Restricted
    "knowledge_base":        {"dims": 3072, "distance": "Cosine"},
    # ... 13 collections total
}

# Access control levels (Chapter 6 + Chapter 12)
SYSTEM_ONLY_COLLECTIONS = {"opportunities_raw"}
RESTRICTED_RAG_COLLECTIONS = {"commercial_catalog", "project_history"}


# =============================================================================
# Chunking strategies by document type (Chapter 12)
# =============================================================================

CHUNKING_CONFIG = {
    # Continuous text: recursive splitting works well
    "propuesta_tecnica": {"chunk_size": 800, "chunk_overlap": 150},
    "informe_analisis":  {"chunk_size": 800, "chunk_overlap": 150},
    "normativa":         {"chunk_size": 800, "chunk_overlap": 150},

    # Tabular documents: each table is an atomic unit
    "presupuesto":       {"strategy": "table_atomic"},

    # Contractual: chunk by clause number, not by length
    "contrato":          {"strategy": "clause_boundary", "pattern": r"\d+\.\d*\s+[A-Z]"},

    # CVs: chunk by section (experience, education, skills)
    "cv_profile":        {"strategy": "section_boundary"},

    # Meeting notes: chunk by agenda item
    "acta_reunion":      {"strategy": "agenda_item"},
}


# =============================================================================
# Document loader (Chapter 12)
# =============================================================================

class DocumentLoader:
    """
    Loads documents based on MIME type with OCR fallback for scanned PDFs.

    Supported formats: PDF, DOCX, XLSX, PPTX.
    Uses LangChain's Unstructured loaders in 'elements' mode to preserve
    document structure (titles, paragraphs, tables as separate elements).
    """

    def compute_hash(self, file_path: str) -> str:
        """SHA-256 for deduplication and integrity."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def is_scanned_pdf(self, file_path: str) -> bool:
        """
        Detect if a PDF is primarily image-based (scanned).
        Heuristic: if <10% of pages have selectable text, apply OCR.
        """
        # In production: uses PyMuPDF (fitz)
        # doc = fitz.open(file_path)
        # pages_with_text = sum(
        #     1 for page in doc if len(page.get_text().strip()) > 50
        # )
        # return pages_with_text / max(len(doc), 1) < 0.1
        return False

    def load_document(self, file_path: str, mime_type: str) -> list:
        """
        Load document based on MIME type, with OCR fallback for scanned PDFs.

        Chapter 12: 'elements' mode preserves structure — each title,
        paragraph, table is a separate element. This significantly improves
        chunking quality because the splitter won't cut in the middle
        of a table or mix content from different sections.
        """
        if mime_type == "application/pdf":
            if self.is_scanned_pdf(file_path):
                return self._ocr_pdf(file_path)
            # loader = PyPDFLoader(file_path)
            # return loader.load()
            return []

        elif "wordprocessing" in mime_type or "msword" in mime_type:
            # loader = UnstructuredWordDocumentLoader(file_path, mode="elements")
            # return loader.load()
            return []

        elif "spreadsheet" in mime_type or "ms-excel" in mime_type:
            # loader = UnstructuredExcelLoader(file_path, mode="elements")
            # return loader.load()
            return []

        elif "presentation" in mime_type or "powerpoint" in mime_type:
            # loader = UnstructuredPowerPointLoader(file_path, mode="elements")
            # return loader.load()
            return []

        else:
            raise ValueError(f"Unsupported document type: {mime_type}")

    def _ocr_pdf(self, file_path: str) -> list:
        """
        Extract text from scanned PDFs using Tesseract OCR.
        Requires poppler-utils installed on the system.
        Languages: Spanish + English.
        """
        # In production:
        # pages = pdf2image.convert_from_path(file_path, dpi=300)
        # for i, page_image in enumerate(pages):
        #     text = pytesseract.image_to_string(
        #         page_image, lang="spa+eng", config="--psm 3"
        #     )
        return []


# =============================================================================
# RAG Service (Chapter 12)
# =============================================================================

class RAGService:
    """
    RAG service with collection-level access control.

    Enforces that users can only query collections their role allows
    (Chapter 6 — SecurityContext.can_access_collection).
    """

    def __init__(self, qdrant_host: str = "qdrant", qdrant_port: int = 6333):
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port
        # self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.loader = DocumentLoader()

    def search(
        self,
        query: str,
        collection: str = "operations_general",
        limit: int = 5,
        security_context=None,
    ) -> list:
        """
        Semantic search with access control.

        Chapter 12: Every RAG query checks the user's SecurityContext
        before accessing the collection. A user without permission to
        'commercial_catalog' cannot retrieve those documents, even if
        the query is relevant.
        """
        # Access control check
        if security_context and not security_context.can_access_collection(collection):
            raise PermissionError(
                f"Access denied to collection: {collection}"
            )

        # In production: embed query + search Qdrant
        # embedding = embed_model.embed_query(query)
        # results = self.client.search(
        #     collection_name=collection,
        #     query_vector=embedding,
        #     limit=limit,
        # )
        return []

    def index_document(
        self,
        file_path: str,
        mime_type: str,
        collection: str,
        doc_type: str = "propuesta_tecnica",
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Index a document: load -> chunk -> embed -> store in Qdrant.

        The chunking strategy is selected based on doc_type (Chapter 12):
          - propuesta_tecnica: RecursiveCharacterTextSplitter (800/150)
          - contrato: clause boundary splitting
          - cv_profile: section boundary splitting
          - presupuesto: atomic table units
        """
        # 1. Compute hash for deduplication
        doc_hash = self.loader.compute_hash(file_path)

        # 2. Load document
        documents = self.loader.load_document(file_path, mime_type)

        # 3. Select chunking strategy
        config = CHUNKING_CONFIG.get(doc_type, {"chunk_size": 800, "chunk_overlap": 150})

        # 4. Split into chunks
        # splitter = RecursiveCharacterTextSplitter(
        #     chunk_size=config.get("chunk_size", 800),
        #     chunk_overlap=config.get("chunk_overlap", 150),
        # )
        # chunks = splitter.split_documents(documents)

        # 5. Embed and store
        # vectorstore.add_documents(chunks)

        return {
            "doc_hash": doc_hash,
            "collection": collection,
            "chunks_created": 0,  # len(chunks) in production
        }

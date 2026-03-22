# Extraído de: LibroCISO/cap-11-rag-normativo.md
# Ejemplo didáctico: modelos de datos para gestión de RAG normativo
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel  # Incluye corporate_id, audit, soft delete

class RAGCollection(BaseModel):
    """Colección de vectores en Qdrant.
    Cada colección agrupa documentos por contexto y tipo de embedding."""
    __tablename__ = "rag_collections"

    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    embedding_provider = Column(
        Enum("local", "cloud", name="embedding_provider"),
        nullable=False
    )
    embedding_model = Column(String(100), nullable=False)
    embedding_dimensions = Column(Integer, nullable=False)
    # Ejemplo: "local" + "nomic-embed-text" + 768
    #          "cloud" + "text-embedding-3-large" + 3072
    distance_metric = Column(String(20), default="cosine")
    document_count = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)

    documents = relationship("RAGDocument", back_populates="collection")


class RAGDocument(BaseModel):
    """Documento normativo indexado en una colección RAG.
    Cada documento se divide en N chunks, cada uno con su vector en Qdrant."""
    __tablename__ = "rag_documents"

    collection_id = Column(Integer, ForeignKey("rag_collections.id"), nullable=False)
    title = Column(String(255), nullable=False)       # "RGPD - Reglamento 2016/679"
    source_type = Column(String(50), nullable=False)   # "regulation", "guide", "standard"
    source_authority = Column(String(100))             # "EU", "AEPD", "CCN", "ISO"
    source_url = Column(String(500))                   # URL pública del documento
    publication_date = Column(DateTime)                # Fecha de publicación oficial
    file_path = Column(String(500))                    # Ruta del fichero original
    file_hash = Column(String(64))                     # SHA-256 para detectar cambios
    chunk_size = Column(Integer, default=512)
    chunk_overlap = Column(Integer, default=64)
    total_chunks = Column(Integer, default=0)
    status = Column(
        Enum("pending", "processing", "indexed", "error", name="rag_doc_status"),
        default="pending"
    )
    error_message = Column(Text)

    collection = relationship("RAGCollection", back_populates="documents")

# Extraído de: LibroCISO/cap-11-rag-normativo.md
# Ejemplo didáctico: generación de embeddings e indexación en Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
)
import uuid

class RAGIndexer:
    """Indexa documentos normativos en Qdrant con embeddings configurables."""

    def __init__(self, qdrant_url: str, embedding_service):
        self.client = QdrantClient(url=qdrant_url)
        self.embedding = embedding_service  # Local (Ollama) o cloud (Azure)

    def ensure_collection(self, name: str, dimensions: int):
        """Crea la colección si no existe. Idempotente."""
        collections = [c.name for c in self.client.get_collections().collections]
        if name not in collections:
            self.client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=dimensions,
                    distance=Distance.COSINE,
                ),
            )

    def index_document(
        self,
        collection_name: str,
        chunks: list[dict],
        metadata: dict,  # regulation, article, authority, date...
    ) -> int:
        """Genera embeddings para cada chunk y los inserta en Qdrant.
        Devuelve el número de chunks indexados."""
        points = []
        for chunk in chunks:
            # Generar embedding del texto del chunk
            vector = self.embedding.encode(chunk["text"])

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "text": chunk["text"],
                    "chunk_index": chunk["index"],
                    "word_count": chunk["word_count"],
                    # Metadatos del documento fuente — clave para trazabilidad
                    "regulation": metadata.get("regulation", "unknown"),
                    "article": metadata.get("article", ""),
                    "section": metadata.get("section", ""),
                    "authority": metadata.get("authority", ""),
                    "publication_date": metadata.get("publication_date", ""),
                    "document_title": metadata.get("title", ""),
                    "source_url": metadata.get("source_url", ""),
                },
            )
            points.append(point)

        # Upsert en lotes de 100 para no saturar Qdrant
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=collection_name,
                points=batch,
            )

        return len(points)

    def delete_document_chunks(self, collection_name: str, document_title: str):
        """Elimina todos los chunks de un documento antes de re-indexar."""
        self.client.delete(
            collection_name=collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="document_title",
                        match=MatchValue(value=document_title),
                    )
                ]
            ),
        )

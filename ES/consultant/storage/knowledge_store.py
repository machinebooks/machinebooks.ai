# Extraído de: LibroConsultor/cap-17-memoria-institucional.md
# storage/knowledge_store.py — Almacenamiento vectorial con Qdrant
from qdrant_client import QdrantClient, models
import anthropic
import hashlib

# Conexión a Qdrant local (datos bajo nuestro control)
qdrant = QdrantClient(host="localhost", port=6333)
claude = anthropic.Anthropic()

COLLECTION_NAME = "knowledge_base"

def init_collection():
    """Crea la colección con índices para filtrado por metadatos."""
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=1024,  # Dimensión del embedding
            distance=models.Distance.COSINE
        ),
    )

def store_fragment(fragment: dict, embedding: list[float]):
    """Almacena un fragmento con su embedding y metadatos."""
    fragment_id = hashlib.md5(
        fragment["content"].encode()
    ).hexdigest()

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[models.PointStruct(
            id=fragment_id,
            vector=embedding,
            payload={
                "type": fragment["type"],
                "context": fragment["context"],
                "content": fragment["content"],
                "result": fragment.get("result", ""),
                "conditions": fragment.get("conditions", ""),
                "sector": fragment["tags"].get("sector", []),
                "dominio": fragment["tags"].get("dominio", []),
                "tipo_proyecto": fragment["tags"].get("tipo_proyecto", []),
                "tecnologias": fragment["tags"].get("tecnologias", []),
                "resultado": fragment["tags"].get("resultado", "desconocido"),
                "relevancia": fragment["tags"].get("relevancia", 3),
                "doc_id": fragment.get("doc_id", ""),
                "created_at": fragment.get("created_at", ""),
            }
        )]
    )

def search_knowledge(
    query: str,
    query_embedding: list[float],
    filters: dict = None,
    top_k: int = 10
) -> list[dict]:
    """Busca fragmentos relevantes con filtros opcionales."""
    # Construir filtros de Qdrant
    must_conditions = []
    if filters:
        if "sector" in filters:
            must_conditions.append(
                models.FieldCondition(
                    key="sector",
                    match=models.MatchAny(any=filters["sector"])
                )
            )
        if "dominio" in filters:
            must_conditions.append(
                models.FieldCondition(
                    key="dominio",
                    match=models.MatchAny(any=filters["dominio"])
                )
            )
        if "relevancia_min" in filters:
            must_conditions.append(
                models.FieldCondition(
                    key="relevancia",
                    range=models.Range(gte=filters["relevancia_min"])
                )
            )

    search_filter = models.Filter(must=must_conditions) if must_conditions else None

    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        query_filter=search_filter,
        limit=top_k,
        score_threshold=0.65  # Umbral de similitud mínima
    )

    return [
        {**hit.payload, "score": hit.score}
        for hit in results
    ]

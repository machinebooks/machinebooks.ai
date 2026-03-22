# Extraído de: LibroConsultor/cap-01-crisis-consultoria.md
from qdrant_client import QdrantClient, models
import anthropic

# Configuración del cliente Qdrant
qdrant = QdrantClient(host="localhost", port=6333)

# Configuración del cliente Anthropic para embeddings
anth_client = anthropic.Anthropic(api_key="<TU_ANTHROPIC_KEY>")

def index_document(doc_id: str, text: str, metadata: dict):
    """Indexa un documento de la práctica en el knowledge base."""

    # Dividir en chunks de ~500 palabras con solapamiento
    chunks = split_into_chunks(text, chunk_size=500, overlap=50)

    points = []
    for i, chunk in enumerate(chunks):
        # Generar embedding con el modelo de Anthropic
        embedding = generate_embedding(chunk)

        points.append(models.PointStruct(
            id=f"{doc_id}_chunk_{i}",
            vector=embedding,
            payload={
                "text": chunk,
                "doc_id": doc_id,
                "doc_type": metadata.get("type"),     # "propuesta", "auditoria", "leccion"
                "sector": metadata.get("sector"),       # "publico", "financiero", "industria"
                "framework": metadata.get("framework"), # "ISO27001", "ENS", "DORA"
                "resultado": metadata.get("resultado"), # "ganada", "perdida", "en_curso"
                "fecha": metadata.get("fecha"),
                "chunk_index": i
            }
        ))

    qdrant.upsert(collection_name="conocimiento_consultoria", points=points)

def search_relevant_experience(query: str, filters: dict = None, limit: int = 10):
    """Busca experiencia previa relevante para el contexto actual."""

    query_embedding = generate_embedding(query)

    # Construir filtros opcionales
    search_filter = None
    if filters:
        conditions = []
        if "sector" in filters:
            conditions.append(
                models.FieldCondition(
                    key="sector",
                    match=models.MatchValue(value=filters["sector"])
                )
            )
        if "resultado" in filters:
            conditions.append(
                models.FieldCondition(
                    key="resultado",
                    match=models.MatchValue(value=filters["resultado"])
                )
            )
        if conditions:
            search_filter = models.Filter(must=conditions)

    results = qdrant.search(
        collection_name="conocimiento_consultoria",
        query_vector=query_embedding,
        query_filter=search_filter,
        limit=limit
    )
    return results

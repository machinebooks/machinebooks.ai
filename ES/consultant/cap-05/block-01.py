# Extraído de: LibroConsultor/cap-05-agentes-analisis.md
from qdrant_client import QdrantClient
import voyageai

qdrant = QdrantClient(host="localhost", port=6333)
voyage = voyageai.Client()

@tool
def search_evidence(
    query: str,
    doc_types: list[str] | None = None,
    max_results: int = 5
) -> list[dict]:
    """Busca evidencias en la documentación del cliente relevantes
    para un control o requisito específico.

    Args:
        query: Descripción del control o requisito a evaluar
        doc_types: Tipos de documento a buscar (politica, procedimiento,
                   registro, informe). None busca en todos.
        max_results: Número máximo de resultados
    """
    # Genera embedding de la consulta
    embedding = voyage.embed(
        texts=[query],
        model="voyage-3"
    ).embeddings[0]

    # Construye filtros por tipo de documento
    search_filter = None
    if doc_types:
        search_filter = {
            "must": [{"key": "doc_type", "match": {"any": doc_types}}]
        }

    # Busca en la colección del cliente activo
    results = qdrant.search(
        collection_name="client_evidence",
        query_vector=embedding,
        query_filter=search_filter,
        limit=max_results
    )

    return [
        {
            "content": hit.payload["content"],
            "source": hit.payload["source_doc"],
            "doc_type": hit.payload["doc_type"],
            "page": hit.payload.get("page", "N/A"),
            "relevance_score": round(hit.score, 3)
        }
        for hit in results
    ]

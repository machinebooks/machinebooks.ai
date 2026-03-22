# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
import anthropic
from typing import Any

# Herramienta de búsqueda en el sistema RAG
def search_documents(
    query: str,
    collection: str = "operations_general",
    max_results: int = 5
) -> dict[str, Any]:
    """
    Busca documentos relevantes en el sistema RAG de la Plataforma.

    Args:
        query: Consulta en lenguaje natural
        collection: Colección Qdrant a consultar (por defecto: operations_general)
        max_results: Número máximo de resultados a retornar (1-10)

    Returns:
        Dict con lista de fragmentos y metadatos
    """
    # La implementación real consulta el servicio Qdrant
    results = rag_service.search(
        query=query,
        collection=collection,
        limit=max_results
    )
    return {
        "fragments": [r.to_dict() for r in results],
        "total_found": len(results),
        "collection": collection
    }

# Herramienta de búsqueda textual en Meilisearch
def search_opportunities(
    keywords: str,
    budget_min: float = None,
    budget_max: float = None,
    category: str = None
) -> dict[str, Any]:
    """
    Busca oportunidades en el índice Meilisearch con filtros opcionales.
    """
    # Lista blanca de categorías válidas — previene filter injection en Meilisearch
    VALID_CATEGORIES = {"energia", "industria", "servicios", "tecnologia", "infraestructura"}

    filters = []
    if budget_min:
        filters.append(f"budget_amount >= {budget_min}")
    if category:
        if category.lower() not in VALID_CATEGORIES:
            raise ValueError(f"Categoría no permitida: {category}")
        filters.append(f"category = '{category}'")

    results = meilisearch_service.search(
        index="opportunities",
        query=keywords,
        filters=" AND ".join(filters) if filters else None,
        limit=10
    )
    return {"opportunities": results, "total": results.total}

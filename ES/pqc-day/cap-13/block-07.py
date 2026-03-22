# Extraído de: LibroPQC/cap-13-rag.md
def search_knowledge_base(
    query: str,
    collection_types: list = None,
    max_results: int = 3
) -> dict:
    """
    Tool del agente: buscar en la base de conocimiento RAG.

    El agente invoca esta herramienta cuando necesita contexto
    regulatorio para fundamentar una recomendación de migración.

    Args:
        query: Pregunta o contexto de búsqueda
        collection_types: Filtro por tipo de colección
        max_results: Número máximo de fragmentos a devolver

    Returns:
        dict con fragmentos relevantes y metadatos de origen
    """
    from app.services.rag_search import RAGSearchService

    service = RAGSearchService()
    results = service.search(
        query=query,
        collection_types=collection_types or [
            'documentation', 'framework'
        ],
        max_chunks=max_results
    )

    return {
        "found": len(results),
        "chunks": [
            {
                "text": r["text"][:1500],  # Limitar tamaño
                "source": r.get("source_title", "Unknown"),
                "url": r.get("source_url", ""),
                "type": r.get("collection_type", "custom"),
            }
            for r in results
        ]
    }

# Registro como tool del agente con esquema JSON
TOOL_SEARCH_KNOWLEDGE = {
    "name": "search_knowledge_base",
    "description": (
        "Buscar en la base de conocimiento de estándares PQC, "
        "regulaciones (NIS2, DORA, CNSA 2.0) y guías ENISA. "
        "Usar cuando se necesite fundamentar una recomendación "
        "con una referencia regulatoria o técnica verificada."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Consulta de búsqueda"
            },
            "collection_types": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Tipos: documentation, framework, policy"
            },
            "max_results": {
                "type": "integer",
                "default": 3
            }
        },
        "required": ["query"]
    }
}

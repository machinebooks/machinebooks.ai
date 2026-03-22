# Extraído de: LibroConsultor/cap-06-generacion-entregables.md
def enrich_with_rag_context(
    self, section_id: str, query: str, filters: dict
) -> str:
    """Busca contexto relevante en la base de conocimiento."""
    # Consultar Qdrant con filtros de tipo y sector
    results = self.rag_client.search(
        query=query,
        filters={
            "document_type": ["informe", "leccion_aprendida"],
            "sector": filters.get("sector", None),
            "framework": filters.get("framework", None),
        },
        top_k=5,
    )

    if not results:
        return ""

    # Formatear contexto para inyección
    context_parts = []
    for r in results:
        context_parts.append(
            f"[Fuente: {r.metadata['document_type']}, "
            f"{r.metadata['year']}]\n{r.text}"
        )
    return "\n---\n".join(context_parts)

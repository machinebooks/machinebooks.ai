# Extraído de: LibroConsultor/cap-04-rag-conocimiento.md
def search_knowledge(query: str, top_k: int = 5) -> list[dict]:
    """Búsqueda semántica con filtros extraídos automáticamente."""
    filters = extract_search_filters(query)

    # Generar embedding de la consulta
    query_embedding = voyage.embed(
        [query], model=EMBEDDING_MODEL
    ).embeddings[0]

    # Construir filtros de Qdrant
    must_conditions = []
    for key, value in filters.items():
        if key == "year_min":
            must_conditions.append(
                models.FieldCondition(
                    key="metadata.year",
                    range=models.Range(gte=value)
                )
            )
        elif key == "year_max":
            must_conditions.append(
                models.FieldCondition(
                    key="metadata.year",
                    range=models.Range(lte=value)
                )
            )
        else:
            must_conditions.append(
                models.FieldCondition(
                    key=f"metadata.{key}",
                    match=models.MatchValue(value=value)
                )
            )

    query_filter = (
        models.Filter(must=must_conditions)
        if must_conditions else None
    )

    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        query_filter=query_filter,
        limit=top_k,
        with_payload=True
    )
    return [
        {
            "text": hit.payload["text"],
            "score": hit.score,
            "section": hit.payload["section"],
            "metadata": hit.payload["metadata"]
        }
        for hit in results
    ]

# Extraído de: LibroTecnico/cap-12-rag-produccion.md
def query_rag_with_access_control(
    query: str,
    collection_name: str,
    user_id: int,
    user_roles: list[str],
    embeddings_model,
    qdrant_client,
    k: int = 5,
) -> list[dict]:
    """
    Consulta RAG con filtro de acceso por usuario y rol.
    Solo devuelve fragmentos de documentos a los que el usuario tiene acceso
    y que son la versión actual del documento.
    """
    query_embedding = embeddings_model.embed_query(query)

    # Filtro compuesto: versión actual + (propietario O rol permitido)
    access_filter = Filter(
        must=[
            FieldCondition(
                key="is_current_version",
                match=MatchValue(value=True),
            )
        ],
        should=[
            FieldCondition(
                key="owner_user_id",
                match=MatchValue(value=user_id),
            ),
            *[
                FieldCondition(
                    key="allowed_roles",
                    match=MatchValue(value=role),
                )
                for role in user_roles
            ]
        ],
        minimum_should_match=1,
    )

    results = qdrant_client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        query_filter=access_filter,
        limit=k,
        with_payload=True,
        score_threshold=0.72,  # Umbral mínimo de similitud coseno
    )

    return [
        {
            "text": hit.payload["text"],
            "document_id": hit.payload["document_id"],
            "document_type": hit.payload["document_type"],
            "score": hit.score,
            "source_page": hit.payload.get("source_page"),
        }
        for hit in results
    ]

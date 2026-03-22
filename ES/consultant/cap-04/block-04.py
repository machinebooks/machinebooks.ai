# Extraído de: LibroConsultor/cap-04-rag-conocimiento.md
def create_collection():
    """Crea la colección con índices para filtrado eficiente."""
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=1024,           # dimensiones de voyage-3
            distance=models.Distance.COSINE
        )
    )
    # Índices para filtrado por metadatos
    for field_name in ["tipo", "sector", "year", "framework", "resultado"]:
        qdrant.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name=f"metadata.{field_name}",
            field_schema=models.PayloadSchemaType.KEYWORD
            if field_name != "year"
            else models.PayloadSchemaType.INTEGER
        )


def ingest_chunks(chunks: list[dict]) -> int:
    """Indexa fragmentos en Qdrant, evitando duplicados."""
    existing_hashes = get_existing_hashes()  # consulta Qdrant
    new_chunks = [c for c in chunks if c["doc_hash"] not in existing_hashes]

    if not new_chunks:
        return 0

    # Generar embeddings en batch (máx 128 por llamada)
    texts = [c["text"] for c in new_chunks]
    embeddings = []
    for i in range(0, len(texts), 128):
        batch = texts[i:i + 128]
        result = voyage.embed(batch, model=EMBEDDING_MODEL)
        embeddings.extend(result.embeddings)

    # Insertar en Qdrant
    points = [
        models.PointStruct(
            id=idx,
            vector=emb,
            payload={
                "text": chunk["text"],
                "section": chunk["section"],
                "metadata": chunk["metadata"],
                "doc_hash": chunk["doc_hash"]
            }
        )
        for idx, (chunk, emb) in enumerate(
            zip(new_chunks, embeddings), start=get_next_id()
        )
    ]
    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    return len(points)

# Extraído de: LibroAIGateway/cap-12-cola-rag.md
# gateway/app/services/rag_service.py:817-977 (flujo principal, sintetizado)
async def search(cls, collection_name, query, db, top_k, threshold, log_context=None):
    # 1. Embedding de la query (con cache)
    query_vector, _ = await EmbeddingCacheService.embed_query_cached(...)

    # 2. Búsqueda vectorial (overfetch: top_k * 2)
    hits = await store.search(query_vector, top_k=top_k*2, threshold=threshold)

    # 3. Enriquecer con datos de DB (solo chunks de docs activos)
    chunks = await db.execute(select(RAGChunk).join(RAGDocument)...)
    enriched = [{content, score, chunk_id, token_count} ...]

    # 4. Keyword fallback (LIKE en MySQL)
    keyword_matches = await cls._search_keyword_matches(collection, query, db, top_k)

    # 5. Merge: mejor score gana por chunk_id
    merged = {chunk_id: best(item) for item in enriched + keyword_matches}

    # 6. Dedup por SHA-256 del contenido normalizado
    seen_hashes = set()
    deduped = []
    for item in sorted(merged.values(), key=lambda x: x["score"], reverse=True):
        h = sha256(item["content"].strip().lower().encode())
        if h not in seen_hashes:
            deduped.append(item)
            seen_hashes.add(h)
        if len(deduped) >= top_k:
            break
    return deduped

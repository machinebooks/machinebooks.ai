# Extracted from: LibroAIGateway/cap-12-queue-rag.md
# gateway/app/services/rag_service.py:817-977 (main flow, synthesized)
async def search(cls, collection_name, query, db, top_k, threshold, log_context=None):
    # 1. Query embedding (with cache)
    query_vector, _ = await EmbeddingCacheService.embed_query_cached(...)

    # 2. Vector search (overfetch: top_k * 2)
    hits = await store.search(query_vector, top_k=top_k*2, threshold=threshold)

    # 3. Enrich with DB data (only chunks from active docs)
    chunks = await db.execute(select(RAGChunk).join(RAGDocument)...)
    enriched = [{content, score, chunk_id, token_count} ...]

    # 4. Keyword fallback (LIKE in MySQL)
    keyword_matches = await cls._search_keyword_matches(collection, query, db, top_k)

    # 5. Merge: best score wins per chunk_id
    merged = {chunk_id: best(item) for item in enriched + keyword_matches}

    # 6. Dedup by SHA-256 of normalized content
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

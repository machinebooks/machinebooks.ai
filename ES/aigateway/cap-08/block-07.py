# Extraído de: LibroAIGateway/cap-08-caching.md
# gateway/app/services/semantic_cache_service.py:106-182 (sintetizado)
async def lookup(db, *, purpose: str, model: str, messages: list[dict],
                 embedding_config: dict, threshold: float = 0.97):
    query = _extract_user_query(messages)
    if not query or len(query) < 8:
        return None, None

    # 1. Exacto por SHA-256 como atajo (misma query literal)
    exact = await db.execute(
        select(SemanticCacheEntry).where(
            SemanticCacheEntry.query_sha256 == sha256(query),
            SemanticCacheEntry.model == model,
            SemanticCacheEntry.purpose == purpose,
        )
    )
    if exact_row := exact.scalar_one_or_none():
        return json.loads(exact_row.response_json), 1.0

    # 2. Scan lineal de las 500 entradas más recientes para (purpose, model)
    candidates = await db.execute(
        select(SemanticCacheEntry)
        .where(SemanticCacheEntry.purpose == purpose,
               SemanticCacheEntry.model == model)
        .order_by(SemanticCacheEntry.last_used.desc())
        .limit(500)
    )

    query_vec = await EmbeddingService.embed_query(query, embedding_config)
    for entry in candidates:
        entry_vec = json.loads(entry.query_embedding_json)
        sim = _cosine(query_vec, entry_vec)
        if sim >= threshold:
            return json.loads(entry.response_json), sim

    return None, None

# Extraído de: LibroAIGateway/cap-09-compresion-tokens.md
# gateway/app/services/compression/bm25.py:34-51 (sintetizado)
def bm25_score_messages(
    query: str,
    messages: List[dict],
    k1: float = 1.5,       # saturación de frecuencia de término
    b: float = 0.75,       # normalización por longitud del documento
) -> List[float]:
    """Score por mensaje usando Okapi BM25 puro."""
    query_terms = _tokenize(query)
    # ... tokenización, IDF, scoring ...
    for term in query_terms:
        tf = _expand_tf(term, tf_counts)  # prefix expansion
        numerator = tf * (k1 + 1)
        denominator = tf + k1 * (1 - b + b * dl / avgdl)
        score += idf[term] * numerator / denominator

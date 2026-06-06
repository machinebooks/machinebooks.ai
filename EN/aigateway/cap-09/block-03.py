# Extracted from: LibroAIGateway/cap-09-compression-tokens.md
# gateway/app/services/compression/bm25.py:34-51 (synthesized)
def bm25_score_messages(
    query: str,
    messages: List[dict],
    k1: float = 1.5,       # term frequency saturation
    b: float = 0.75,       # document length normalization
) -> List[float]:
    """Score per message using pure Okapi BM25."""
    query_terms = _tokenize(query)
    # ... tokenization, IDF, scoring ...
    for term in query_terms:
        tf = _expand_tf(term, tf_counts)  # prefix expansion
        numerator = tf * (k1 + 1)
        denominator = tf + k1 * (1 - b + b * dl / avgdl)
        score += idf[term] * numerator / denominator

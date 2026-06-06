# Extracted from: LibroAIGateway/cap-09-compression-tokens.md
# gateway/app/services/compression/bm25.py:87-98
def _expand_tf(query_term: str, tf_counts: Counter) -> int:
    """Sum TF across doc tokens prefixed by query_term (min 4 chars)."""
    exact = tf_counts.get(query_term, 0)
    if exact:
        return exact
    if len(query_term) < 4:
        return 0
    return sum(
        count for token, count in tf_counts.items()
        if token != query_term and token.startswith(query_term)
    )

# Extraído de: LibroAIGateway/cap-12-cola-rag.md
# gateway/app/api/v1/llm_queued.py:94-115
def _sanitize_error(raw: Any) -> str:
    """Devuelve un mensaje genérico, NO traceback ni detalle interno."""
    msg = str(raw or "").lower()
    if "429" in msg or "rate" in msg or "limit" in msg or "quota" in msg:
        return "rate_limit"
    if "content_filter" in msg or "safety" in msg or "policy" in msg:
        return "content_filter"
    if "timeout" in msg or "timed out" in msg:
        return "timeout"
    if "connection" in msg or "network" in msg:
        return "network"
    if "context_length" in msg or "context window" in msg:
        return "context_length"
    if "auth" in msg or "401" in msg or "403" in msg:
        return "auth"
    return "internal_error"

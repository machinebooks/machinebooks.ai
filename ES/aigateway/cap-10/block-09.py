# Extraído de: LibroAIGateway/cap-10-embeddings-imagenes-audio.md
# gateway/app/services/embedding_service.py:113-126
def _is_retryable_embedding_error(exc: Exception) -> bool:
    if isinstance(exc, (httpx.TimeoutException, httpx.ConnectError, ...)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        sc = exc.response.status_code
        return sc == 429 or 500 <= sc < 600
    return False

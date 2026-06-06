# Extraído de: LibroAIGateway/cap-09-compresion-tokens.md
# gateway/app/services/token_counter.py:35-52 (sintetizado)
@lru_cache(maxsize=8)
def _get_encoding(model: str | None):
    try:
        import tiktoken
    except ImportError:
        return None  # fallback a char/4

    if model:
        try:
            return tiktoken.encoding_for_model(model)
        except Exception:
            pass  # modelo no soportado por tiktoken
    return tiktoken.get_encoding("cl100k_base")  # fallback encoding

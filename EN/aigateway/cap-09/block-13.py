# Extracted from: LibroAIGateway/cap-09-compression-tokens.md
# gateway/app/services/token_counter.py:35-52 (synthesized)
@lru_cache(maxsize=8)
def _get_encoding(model: str | None):
    try:
        import tiktoken
    except ImportError:
        return None  # fallback to char/4

    if model:
        try:
            return tiktoken.encoding_for_model(model)
        except Exception:
            pass  # model not supported by tiktoken
    return tiktoken.get_encoding("cl100k_base")  # fallback encoding

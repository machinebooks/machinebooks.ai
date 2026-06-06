# Extraído de: LibroAIGateway/cap-07-adapters.md
cache_key = _compute_prompt_cache_key(messages, request.tools, min_chars=800)
if cache_key:
    extra_body = create_kwargs.setdefault("extra_body", {})
    extra_body["prompt_cache_key"] = cache_key

# Extraído de: LibroAIGateway/cap-08-caching.md
# gateway/app/adapters/openai_adapter.py:173-186 (sintetizado)
cached_tokens = 0
prompt_details = getattr(response.usage, "prompt_tokens_details", None)
if prompt_details is not None:
    cached_tokens = getattr(prompt_details, "cached_tokens", 0) or 0
return ChatResponse(
    content=choice.message.content,
    prompt_tokens=response.usage.prompt_tokens,
    completion_tokens=response.usage.completion_tokens,
    cached_tokens=cached_tokens,
    prompt_cache_key=cache_key,
)

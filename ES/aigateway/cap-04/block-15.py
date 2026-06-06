# Extraído de: LibroAIGateway/cap-04-streaming-sse.md
# Dentro del bucle async for chunk in upstream:
if chunk.prompt_tokens is not None:
    prompt_tokens = chunk.prompt_tokens
if chunk.completion_tokens is not None:
    completion_tokens = chunk.completion_tokens
if chunk.cached_tokens is not None:
    ctx.cached_tokens = chunk.cached_tokens

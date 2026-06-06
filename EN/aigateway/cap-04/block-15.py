# Extracted from: LibroAIGateway/cap-04-streaming-sse.md
# Inside the async for chunk in upstream loop:
if chunk.prompt_tokens is not None:
    prompt_tokens = chunk.prompt_tokens
if chunk.completion_tokens is not None:
    completion_tokens = chunk.completion_tokens
if chunk.cached_tokens is not None:
    ctx.cached_tokens = chunk.cached_tokens

# Extraído de: LibroAIGateway/cap-04-streaming-sse.md
async with asyncio.timeout(UPSTREAM_STREAM_TIMEOUT_SECONDS):
    async for chunk in upstream:
        ...

# Extracted from: LibroAIGateway/cap-04-streaming-sse.md
@abstractmethod
async def stream_chat(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
    """SSE streaming call."""
    ...

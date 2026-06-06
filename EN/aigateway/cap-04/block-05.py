# Extracted from: LibroAIGateway/cap-04-streaming-sse.md
return StreamingResponse(
    stream_responses(ctx),
    media_type="text/event-stream",
    headers=stream_headers,
)

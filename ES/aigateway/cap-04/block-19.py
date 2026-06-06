# Extraído de: LibroAIGateway/cap-04-streaming-sse.md
rolling_buffer = (rolling_buffer + chunk.delta)[-512:]
blocked, replacement = await security_output.scan_streaming_chunk(
    ctx, chunk.delta, rolling_buffer,
)

# Extracted from: LibroAIGateway/cap-04-streaming-sse.md
if ctx.cache_hit:
    await audit.run_cache_hit(ctx)
    return StreamingResponse(
        _replay_responses_cache(ctx),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            **(ctx.response_headers or {}),
        },
    )

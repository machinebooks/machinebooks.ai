# Extracted from: LibroAIGateway/cap-04-streaming-sse.md
# Inside the POST /v1/chat/completions endpoint
if not chat_req.stream:
    return await PipelineRunner.run(ctx)

# Streaming: prepare context and pick the right generator
await PipelineRunner._prepare_for_stream(ctx)
generator = (
    _replay_responses_cache(ctx) if ctx.cache_hit
    else stream_responses(ctx)
)
return StreamingResponse(generator, media_type="text/event-stream",
                         headers=ctx.response_headers)

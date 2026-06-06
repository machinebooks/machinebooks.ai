# Extraído de: LibroAIGateway/cap-04-streaming-sse.md
# Dentro del endpoint POST /v1/chat/completions
if not chat_req.stream:
    return await PipelineRunner.run(ctx)

# Streaming: preparar contexto y elegir el generador adecuado
await PipelineRunner._prepare_for_stream(ctx)
generator = (
    _replay_responses_cache(ctx) if ctx.cache_hit
    else stream_responses(ctx)
)
return StreamingResponse(generator, media_type="text/event-stream",
                         headers=ctx.response_headers)

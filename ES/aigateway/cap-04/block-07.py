# Extraído de: LibroAIGateway/cap-04-streaming-sse.md
@classmethod
async def _prepare_for_stream(cls, ctx: PipelineContext) -> None:
    # Stages pre-adapter: se ejecutan secuencialmente
    await auth.run(ctx)
    await hooks.pre_chat(ctx)
    if not await security_input.run(ctx):
        raise HTTPException(403, detail="Solicitud bloqueada por seguridad")
    await filter_stage.run(ctx)
    await hooks.pii_detected(ctx)
    await reduce.run(ctx)
    # ... route, enrich, finalize ...
    ctx.chat_req = await _build_chat_request(ctx)
    ctx.start_time = time.time()
    # El endpoint construye el StreamingResponse con stream_responses(ctx)

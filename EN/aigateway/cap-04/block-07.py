# Extracted from: LibroAIGateway/cap-04-streaming-sse.md
@classmethod
async def _prepare_for_stream(cls, ctx: PipelineContext) -> None:
    # Pre-adapter stages: executed sequentially
    await auth.run(ctx)
    await hooks.pre_chat(ctx)
    if not await security_input.run(ctx):
        raise HTTPException(403, detail="Request blocked by security")
    await filter_stage.run(ctx)
    await hooks.pii_detected(ctx)
    await reduce.run(ctx)
    # ... route, enrich, finalize ...
    ctx.chat_req = await _build_chat_request(ctx)
    ctx.start_time = time.time()
    # The endpoint builds the StreamingResponse with stream_responses(ctx)

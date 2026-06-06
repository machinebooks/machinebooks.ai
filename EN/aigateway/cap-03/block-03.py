# Extracted from: LibroAIGateway/cap-03-pipeline-stages.md
@classmethod
async def run(cls, ctx: PipelineContext) -> dict:
    """Executes the full pipeline for a non-streaming request."""
    try:
        return await cls._run_inner(ctx)
    finally:
        # PHASE P: release the request_rate_limiter gauge
        # even if the request failed. If never acquired, no-op.
        acquired = getattr(ctx, "rate_limit_acquired", None) or []
        if acquired:
            try:
                await _rrl_release(acquired)
            except Exception:
                logger.debug("rrl:release_in_finally_failed", exc_info=True)

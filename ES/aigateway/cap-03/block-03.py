# Extraído de: LibroAIGateway/cap-03-pipeline-stages.md
@classmethod
async def run(cls, ctx: PipelineContext) -> dict:
    """Ejecuta el pipeline completo para una petición no-streaming."""
    try:
        return await cls._run_inner(ctx)
    finally:
        # FASE P: liberar el gauge del request_rate_limiter
        # incluso si la request falló. Si nunca acquired, no-op.
        acquired = getattr(ctx, "rate_limit_acquired", None) or []
        if acquired:
            try:
                await _rrl_release(acquired)
            except Exception:
                logger.debug("rrl:release_in_finally_failed", exc_info=True)

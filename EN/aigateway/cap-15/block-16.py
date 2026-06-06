# Extracted from: LibroAIGateway/cap-15-rate-limiting.md
# Post-call hook in pipeline/runner.py:507-510
try:
    from app.services.session_limiters import increment_session_budget
    sess = getattr(ctx, "conversation_id", None)
    await increment_session_budget(sess, float(ctx.cost_usd or 0))
except Exception as exc:
    logger.debug("session_budget:incr_post_call_failed err=%s", exc)

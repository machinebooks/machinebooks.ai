# Extracted from: LibroAIGateway/cap-04-streaming-sse.md
finally:
    # 1. Close upstream whatever happens
    if upstream is not None and hasattr(upstream, "aclose"):
        with contextlib.suppress(Exception):
            await upstream.aclose()

    # 2. Post-stream security before persisting
    sanitized = await _apply_post_stream_security(ctx, full_content)
    if sanitized:
        ctx.response_text = sanitized

    # 3. Total latency
    ctx.latency_ms = int((time.time() - ctx.start_time) * 1000)

    # 4. Audit — protected so it does not mask errors
    try:
        await audit.run(ctx, prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens)
    except Exception:
        logger.exception("pipeline:stream:audit_failed")

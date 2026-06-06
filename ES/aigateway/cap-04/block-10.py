# Extraído de: LibroAIGateway/cap-04-streaming-sse.md
finally:
    # ... cerrar upstream ...
    sanitized = await _apply_post_stream_security(ctx, full_content)
    if sanitized:
        ctx.response_text = sanitized
    # ...
    try:
        await audit.run(ctx, ...)
    except Exception:
        logger.exception("pipeline:stream:audit_failed")

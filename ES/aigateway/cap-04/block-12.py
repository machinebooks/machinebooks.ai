# Extraído de: LibroAIGateway/cap-04-streaming-sse.md
finally:
    # 1. Cerrar upstream pase lo que pase
    if upstream is not None and hasattr(upstream, "aclose"):
        with contextlib.suppress(Exception):
            await upstream.aclose()

    # 2. Post-stream security antes de persistir
    sanitized = await _apply_post_stream_security(ctx, full_content)
    if sanitized:
        ctx.response_text = sanitized

    # 3. Latencia total
    ctx.latency_ms = int((time.time() - ctx.start_time) * 1000)

    # 4. Audit — protegido para no enmascarar errores
    try:
        await audit.run(ctx, prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens)
    except Exception:
        logger.exception("pipeline:stream:audit_failed")

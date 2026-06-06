# Extraído de: LibroAIGateway/cap-03-pipeline-stages.md
# Test unitario de filter — sin auth, sin route, sin nada
async def test_filter_redacts_pii():
    ctx = PipelineContext(
        request=MockRequest(),
        db=mock_db,
        redis=mock_redis,
        device_id="test-device",
        messages=[{"role": "user", "content": "Mi email es test@ejemplo.com"}],
        org_id=1,
    )
    await filter_stage.run(ctx)
    assert "[EMAIL_REDACTED]" in ctx.sanitized_messages[0]["content"]
    assert ctx.pii_detected > 0

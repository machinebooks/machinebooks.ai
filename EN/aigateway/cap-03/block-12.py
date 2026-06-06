# Extracted from: LibroAIGateway/cap-03-pipeline-stages.md
# Unit test for filter — no auth, no route, nothing
async def test_filter_redacts_pii():
    ctx = PipelineContext(
        request=MockRequest(),
        db=mock_db,
        redis=mock_redis,
        device_id="test-device",
        messages=[{"role": "user", "content": "My email is test@example.com"}],
        org_id=1,
    )
    await filter_stage.run(ctx)
    assert "[EMAIL_REDACTED]" in ctx.sanitized_messages[0]["content"]
    assert ctx.pii_detected > 0

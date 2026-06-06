# Extracted from: LibroAIGateway/cap-10-embeddings-images-audio.md
# gateway/app/api/v1/audio.py:272-297 y 405-430
try:
    await AuditService.log_request(
        db=db, device_id=device_id, employee_id=employee_id,
        provider=model_row.provider if model_row else "azure_openai",
        ...
    )
except Exception as exc:
    logger.warning("tts:audit_log_failed: %s", exc)
# The response is returned anyway

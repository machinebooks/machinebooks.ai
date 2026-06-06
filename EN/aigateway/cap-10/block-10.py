# Extracted from: LibroAIGateway/cap-10-embeddings-images-audio.md
# gateway/app/services/embedding_service.py:230-239
try:
    await cls._audit_embed(config=config, total_tokens=total_tokens, ...)
except Exception as audit_exc:
    logger.warning("embed:audit_failed model=%s tokens=%d err=%s", ...)
return embeddings  # always returned

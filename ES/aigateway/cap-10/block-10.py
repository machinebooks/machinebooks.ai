# Extraído de: LibroAIGateway/cap-10-embeddings-imagenes-audio.md
# gateway/app/services/embedding_service.py:230-239
try:
    await cls._audit_embed(config=config, total_tokens=total_tokens, ...)
except Exception as audit_exc:
    logger.warning("embed:audit_failed model=%s tokens=%d err=%s", ...)
return embeddings  # se devuelven siempre

# Extracted from: LibroAIGateway/cap-10-embeddings-images-audio.md
# gateway/app/api/v1/embeddings.py:109-111
except Exception as exc:
    logger.exception("embeddings:failed model=%s", body.model)
    raise safe_http_exception(502, "ERR_UPSTREAM_PROVIDER")

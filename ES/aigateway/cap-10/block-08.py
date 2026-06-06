# Extraído de: LibroAIGateway/cap-10-embeddings-imagenes-audio.md
# gateway/app/services/embedding_service.py:73-75
_EMBED_CONCURRENCY_DEFAULT = max(1, int(os.environ.get("N7X_EMBED_CONCURRENCY", "8")))
_EMED_SEM: Optional[asyncio.Semaphore] = None

# Source: The FinOps Engineer and the Machine -- Chapter 10
# Pattern: Embedding service with local/API routing

# services/embedding_service.py
import httpx
from typing import Optional

class EmbeddingService:
    """
    Embedding service with local (Ollama) and external API support.
    On the Platform we use local by default: the volume justifies it.
    """

    LOCAL_EMBEDDING_MODEL  = "nomic-embed-text"  # 137M parameters, runs on CPU
    FALLBACK_DIMENSIONS    = 768

    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        use_local: bool = True,
    ):
        self.ollama_url = ollama_url
        self.use_local  = use_local

    def embed(self, text: str) -> list[float]:
        """
        Generates the embedding of a text.
        Uses the local model if available, at zero token cost.
        """
        if self.use_local:
            try:
                return self._embed_local(text)
            except Exception:
                pass  # silent fallback to external API

        return self._embed_api_fallback(text)

    def _embed_local(self, text: str) -> list[float]:
        """Embeddings with Ollama (cost: $0 in tokens)."""
        resp = httpx.post(
            f"{self.ollama_url}/api/embeddings",
            json={"model": self.LOCAL_EMBEDDING_MODEL, "prompt": text},
            timeout=10.0,
        )
        resp.raise_for_status()
        return resp.json()["embedding"]

    def _embed_api_fallback(self, text: str) -> list[float]:
        """
        Fallback to external API if local does not respond.
        In production, log this event in the LLMUsageLog
        with the corresponding cost_usd.
        """
        # External embedding provider fallback implementation
        raise NotImplementedError("Configure external embedding provider")

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generates embeddings in batch for mass indexing.
        No rate limit imposed by an external API.
        """
        return [self.embed(t) for t in texts]

# Extraído de: LibroFinOps/cap-10-selfhosted-vs-api.md
# services/embedding_service.py
import httpx
from typing import Optional

class EmbeddingService:
    """
    Servicio de embeddings con soporte local (Ollama) y API externa.
    En la Plataforma usamos local por defecto: el volumen lo justifica.
    """

    LOCAL_EMBEDDING_MODEL  = "nomic-embed-text"  # 137M parámetros, corre en CPU
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
        Genera el embedding de un texto.
        Usa el modelo local si está disponible, sin coste de tokens.
        """
        if self.use_local:
            try:
                return self._embed_local(text)
            except Exception:
                pass  # fallback silencioso a API externa

        return self._embed_api_fallback(text)

    def _embed_local(self, text: str) -> list[float]:
        """Embeddings con Ollama (coste: $0 en tokens)."""
        resp = httpx.post(
            f"{self.ollama_url}/api/embeddings",
            json={"model": self.LOCAL_EMBEDDING_MODEL, "prompt": text},
            timeout=10.0,
        )
        resp.raise_for_status()
        return resp.json()["embedding"]

    def _embed_api_fallback(self, text: str) -> list[float]:
        """
        Fallback a API externa si el local no responde.
        En producción, registrar este evento en el LLMUsageLog
        con cost_usd correspondiente.
        """
        # Implementación de fallback a proveedor externo de embeddings
        raise NotImplementedError("Configurar proveedor externo de embeddings")

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Genera embeddings en lote para indexación masiva.
        Sin límite de rate impuesto por una API externa.
        """
        return [self.embed(t) for t in texts]

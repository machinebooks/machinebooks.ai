# Extraído de: LibroFinOps/cap-09-cache-prompt-batch.md
# services/semantic_cache.py
import hashlib
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional
import numpy as np

@dataclass
class CacheEntry:
    """Entrada en la caché semántica."""
    query_embedding: list[float]
    query_text: str
    response_text: str
    model: str
    service_name: str
    created_at: datetime
    ttl_hours: int = 24
    hit_count: int = 0

class SemanticCache:
    """
    Caché semántica basada en embeddings y similitud del coseno.
    Complementa el prompt caching de Anthropic para consultas
    semánticamente equivalentes pero textualmente distintas.
    """

    def __init__(
        self,
        embedding_service,
        similarity_threshold: float = 0.93,
        max_entries: int = 10_000,
        default_ttl_hours: int = 24,
    ):
        self.embedder = embedding_service
        self.threshold = similarity_threshold
        self.max_entries = max_entries
        self.default_ttl = default_ttl_hours
        # En producción, usar Redis o Qdrant; aquí simplificamos
        self._entries: list[CacheEntry] = []

    def lookup(
        self, query: str, service_name: str
    ) -> Optional[str]:
        """
        Busca en la caché una respuesta semánticamente equivalente.
        Devuelve la respuesta cacheada o None si no hay hit.
        """
        query_emb = self.embedder.embed(query)
        now = datetime.utcnow()

        best_score = 0.0
        best_entry: Optional[CacheEntry] = None

        for entry in self._entries:
            # Filtrar por servicio y TTL
            if entry.service_name != service_name:
                continue
            if now > entry.created_at + timedelta(hours=entry.ttl_hours):
                continue

            score = self._cosine_similarity(query_emb, entry.query_embedding)
            if score > best_score:
                best_score = score
                best_entry = entry

        if best_entry and best_score >= self.threshold:
            best_entry.hit_count += 1
            return best_entry.response_text

        return None

    def store(
        self,
        query: str,
        response: str,
        model: str,
        service_name: str,
    ):
        """Almacena una nueva entrada en la caché semántica."""
        embedding = self.embedder.embed(query)

        entry = CacheEntry(
            query_embedding=embedding,
            query_text=query,
            response_text=response,
            model=model,
            service_name=service_name,
            created_at=datetime.utcnow(),
            ttl_hours=self.default_ttl,
        )
        self._entries.append(entry)

        # Evictar entradas antiguas si se supera el límite
        if len(self._entries) > self.max_entries:
            self._evict_oldest()

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """Similitud del coseno entre dos vectores."""
        a_np = np.array(a)
        b_np = np.array(b)
        dot = np.dot(a_np, b_np)
        norm = np.linalg.norm(a_np) * np.linalg.norm(b_np)
        return float(dot / norm) if norm > 0 else 0.0

    def _evict_oldest(self):
        """Elimina las entradas más antiguas que exceden el límite."""
        self._entries.sort(key=lambda e: e.created_at)
        self._entries = self._entries[-self.max_entries:]

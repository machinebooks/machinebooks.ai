# Extraído de: LibroPQC/cap-13-rag.md
import anthropic
from typing import List, Dict, Optional

class RAGSearchService:
    """Servicio de búsqueda en colecciones RAG con reranking"""

    def __init__(self):
        self.client = anthropic.Anthropic()

    def search(
        self,
        query: str,
        collection_types: Optional[List[str]] = None,
        max_chunks: int = 5
    ) -> List[Dict]:
        """
        Buscar fragmentos relevantes en la base de conocimiento.

        1. Expandir query con sinónimos criptográficos
        2. Filtrar colecciones por tipo
        3. Buscar por palabras clave (FULLTEXT)
        4. Reranquear con el LLM
        """
        # Paso 1: Expansión de sinónimos criptográficos
        expanded_query = self._expand_crypto_synonyms(query)

        # Paso 2: Filtrar colecciones activas por tipo
        from app.models.ai_admin import AIRAGCollection, AIRAGDocument
        collections_q = AIRAGCollection.query.filter_by(is_active=True)
        if collection_types:
            collections_q = collections_q.filter(
                AIRAGCollection.collection_type.in_(collection_types)
            )
        collection_ids = [c.id for c in collections_q.all()]

        if not collection_ids:
            return []

        # Paso 3: Buscar documentos relevantes
        docs = AIRAGDocument.query.filter(
            AIRAGDocument.collection_id.in_(collection_ids),
            AIRAGDocument.status == 'indexed'
        ).all()

        # Recuperar y puntuar fragmentos
        candidates = self._search_chunks(docs, expanded_query)

        # Paso 4: Reranquear con Claude los top candidatos
        if len(candidates) > max_chunks:
            candidates = self._rerank_with_llm(
                query, candidates[:max_chunks * 3]
            )

        return candidates[:max_chunks]

    def _expand_crypto_synonyms(self, query: str) -> str:
        """Expandir sinónimos de terminología PQC"""
        synonyms = {
            'Kyber': 'Kyber ML-KEM FIPS-203 CRYSTALS-Kyber',
            'ML-KEM': 'ML-KEM Kyber FIPS-203',
            'Dilithium': 'Dilithium ML-DSA FIPS-204 CRYSTALS-Dilithium',
            'ML-DSA': 'ML-DSA Dilithium FIPS-204',
            'SPHINCS+': 'SPHINCS+ SLH-DSA FIPS-205',
            'SLH-DSA': 'SLH-DSA SPHINCS+ FIPS-205',
            'RSA': 'RSA RSA-2048 RSA-4096',
            'ECDSA': 'ECDSA ECC curva-elíptica P-256 P-384',
        }
        expanded = query
        for term, expansion in synonyms.items():
            if term.lower() in query.lower():
                expanded = f"{expanded} {expansion}"
        return expanded

    def _rerank_with_llm(
        self, query: str, candidates: List[Dict]
    ) -> List[Dict]:
        """Reranquear candidatos usando Claude como juez de relevancia"""
        chunks_text = "\n---\n".join([
            f"[{i}] {c['text'][:500]}"
            for i, c in enumerate(candidates)
        ])

        message = self.client.messages.create(
            model="claude-haiku-4-5",  # Modelo rápido para reranking
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": (
                    f"Dada la consulta: '{query}'\n\n"
                    f"Ordena estos fragmentos del más al menos relevante. "
                    f"Responde solo con los índices separados por comas:\n\n"
                    f"{chunks_text}"
                )
            }]
        )

        # Parsear la respuesta del modelo y reordenar
        try:
            indices = [
                int(x.strip())
                for x in message.content[0].text.split(',')
                if x.strip().isdigit()
            ]
            reranked = [candidates[i] for i in indices if i < len(candidates)]
            return reranked if reranked else candidates
        except (ValueError, IndexError):
            return candidates  # Fallback: orden original

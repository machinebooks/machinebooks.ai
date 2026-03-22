# Extraído de: LibroCISO/cap-11-rag-normativo.md
# Ejemplo didáctico: búsqueda semántica en el corpus normativo
from dataclasses import dataclass

@dataclass
class RAGSearchResult:
    """Resultado de búsqueda con texto, metadatos y puntuación."""
    text: str
    score: float          # Similitud coseno (0-1)
    regulation: str       # RGPD, ENS, AEPD, CCN-STIC...
    article: str          # Art. 35, Anexo II, Guía EIPD...
    authority: str        # EU, AEPD, CCN
    document_title: str   # Título completo del documento fuente
    source_url: str       # URL pública para verificación


class RAGSearchService:
    """Servicio de búsqueda semántica sobre corpus normativo."""

    def __init__(self, qdrant_client, embedding_service):
        self.client = qdrant_client
        self.embedding = embedding_service

    def search(
        self,
        query: str,
        collection_name: str = "normative_local",
        top_k: int = 5,
        score_threshold: float = 0.65,
        regulation_filter: str | None = None,
    ) -> list[RAGSearchResult]:
        """Busca chunks relevantes para una consulta regulatoria.

        Args:
            query: Pregunta del usuario en lenguaje natural
            top_k: Número máximo de chunks a devolver
            score_threshold: Similitud mínima para incluir un resultado
            regulation_filter: Filtrar por regulación específica (RGPD, ENS...)
        """
        # 1. Convertir la pregunta en vector
        query_vector = self.embedding.encode(query)

        # 2. Construir filtro opcional por regulación
        search_filter = None
        if regulation_filter:
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="regulation",
                        match=MatchValue(value=regulation_filter),
                    )
                ]
            )

        # 3. Búsqueda por similitud coseno en Qdrant
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            query_filter=search_filter,
            limit=top_k,
            score_threshold=score_threshold,
        )

        # 4. Mapear resultados con metadatos completos
        search_results = []
        for hit in results:
            search_results.append(RAGSearchResult(
                text=hit.payload["text"],
                score=hit.score,
                regulation=hit.payload.get("regulation", "unknown"),
                article=hit.payload.get("article", ""),
                authority=hit.payload.get("authority", ""),
                document_title=hit.payload.get("document_title", ""),
                source_url=hit.payload.get("source_url", ""),
            ))

        return search_results

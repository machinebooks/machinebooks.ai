# Extraído de: LibroConsultor/cap-09-generacion-propuestas.md
import anthropic
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

client_anthropic = anthropic.Anthropic()
qdrant = QdrantClient(url="http://localhost:6333")

COLECCION_PROPUESTAS = "propuestas_secciones"

def recuperar_secciones_similares(
    tipo_seccion: SeccionTipo,
    sector: str,
    tipo_servicio: str,
    descripcion_necesidad: str,
    top_k: int = 5
) -> list[dict]:
    """Recupera secciones de propuestas ganadoras similares."""

    # Generar embedding de la descripción de necesidad
    embedding_response = client_anthropic.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1,
        messages=[{"role": "user", "content": descripcion_necesidad}]
    )
    # En producción: usar endpoint de embeddings dedicado

    # Filtrar por tipo de sección, sector y tipo de servicio
    filtro = Filter(
        must=[
            FieldCondition(
                key="tipo_seccion",
                match=MatchValue(value=tipo_seccion.value)
            ),
            FieldCondition(
                key="sector",
                match=MatchValue(value=sector)
            ),
            FieldCondition(
                key="ganadora",
                match=MatchValue(value=True)
            )
        ]
    )

    resultados = qdrant.search(
        collection_name=COLECCION_PROPUESTAS,
        query_vector=embedding_response,  # Simplificado
        query_filter=filtro,
        limit=top_k,
        with_payload=True
    )

    return [
        {
            "contenido": r.payload["contenido"],
            "sector": r.payload["sector"],
            "tipo_servicio": r.payload["tipo_servicio"],
            "puntuacion": r.payload.get("puntuacion_tecnica", "N/A"),
            "año": r.payload.get("año", "N/A"),
            "score_similitud": r.score
        }
        for r in resultados
    ]

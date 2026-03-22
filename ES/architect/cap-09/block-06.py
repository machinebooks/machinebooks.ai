# Extraído de: LibroTecnico/cap-09-servicios-negocio.md
# Ejemplo didáctico: búsqueda semántica de perfiles de talento
# Patrón: ai_service/services/talent/profile_matcher.py

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny

def find_matching_profiles(
    requirements_text: str,
    family: str,
    seniority_min: str,
    limit: int = 10
) -> list[dict]:
    """
    Busca perfiles que encajan semánticamente con los requisitos de la oportunidad.
    Filtra por familia y seniority mínimo antes de calcular similitud vectorial.
    """
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    # Generar vector de búsqueda desde los requisitos
    query_vector = get_embedding(requirements_text)

    # Filtros estructurales: familia y seniority mínimo
    seniority_levels = ["JUNIOR", "SENIOR", "LEAD", "PRINCIPAL", "DIRECTOR"]
    min_index = seniority_levels.index(seniority_min)
    valid_seniorities = seniority_levels[min_index:]

    results = client.search(
        collection_name="talent_profiles",
        query_vector=query_vector,
        query_filter=Filter(
            must=[
                FieldCondition(key="family", match=MatchValue(value=family)),
                FieldCondition(key="seniority", match=MatchAny(any=valid_seniorities)),
                FieldCondition(key="available", match=MatchValue(value=True)),
            ]
        ),
        limit=limit,
        with_payload=True,
    )

    return [
        {
            "profile_id": hit.id,
            "score": round(hit.score, 3),
            "name": hit.payload["display_name"],
            "seniority": hit.payload["seniority"],
            "specialties": hit.payload["specialties"],
        }
        for hit in results
    ]

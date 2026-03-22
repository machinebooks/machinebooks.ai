# Extraído de: LibroConsultor/cap-19-lecciones-aprendidas.md
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import anthropic
import hashlib
import json

COLLECTION_NAME = "lessons_learned"

def initialize_lessons_collection(qdrant: QdrantClient):
    """Crea la colección de lecciones con esquema de payload."""
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=1024,        # Dimensión del embedding
            distance=Distance.COSINE
        )
    )

def store_validated_lesson(
    lesson: LessonCandidate,
    qdrant: QdrantClient,
    anthropic_client: anthropic.Anthropic
) -> str:
    """Almacena una lección validada con embedding semántico."""
    # Texto combinado para el embedding: resumen + contexto + recomendación
    embedding_text = (
        f"{lesson.summary}\n"
        f"Contexto: {lesson.context}\n"
        f"Causa raíz: {lesson.root_cause}\n"
        f"Recomendación: {lesson.recommendation}"
    )

    # Generar embedding con el modelo de Voyager
    embedding_response = anthropic_client.embeddings.create(
        model="voyage-3",
        input=embedding_text
    )
    vector = embedding_response.data[0].embedding

    # ID determinístico basado en contenido
    lesson_id = hashlib.md5(
        f"{lesson.summary}{lesson.context}".encode()
    ).hexdigest()

    # Payload con metadatos para filtrado estructurado
    payload = {
        "summary": lesson.summary,
        "context": lesson.context,
        "what_happened": lesson.what_happened,
        "root_cause": lesson.root_cause,
        "recommendation": lesson.recommendation,
        "project_type": lesson.project_type,
        "project_phase": lesson.project_phase,
        "category": lesson.category,
        "impact_areas": [ia.value for ia in lesson.impact_areas],
        "polarity": lesson.polarity.value,
        "confidence": lesson.confidence,
        "extraction_date": lesson.extraction_date.isoformat(),
        "validation_status": "validated",
        "times_surfaced": 0,     # Cuántas veces se mostró a un equipo
        "times_useful": 0,       # Cuántas veces el equipo la marcó como útil
        "usefulness_ratio": 0.0  # Ratio de utilidad real
    }

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[PointStruct(
            id=lesson_id,
            vector=vector,
            payload=payload
        )]
    )
    return lesson_id

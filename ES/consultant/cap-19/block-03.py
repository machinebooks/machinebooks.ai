# Extraído de: LibroConsultor/cap-19-lecciones-aprendidas.md
from collections import Counter
from qdrant_client.models import Filter, FieldCondition, MatchValue

PATTERN_DETECTION_PROMPT = """Analiza las siguientes lecciones aprendidas
de múltiples proyectos de consultoría y detecta PATRONES RECURRENTES.

Un patrón válido cumple estos criterios:
1. Aparece en AL MENOS 3 proyectos diferentes
2. Tiene una causa raíz común (no solo síntomas similares)
3. Sugiere una acción SISTÉMICA (no solo un fix puntual)

Para cada patrón, indica:
- Descripción del patrón
- Número de proyectos afectados
- Causa raíz común
- Impacto agregado estimado (horas, coste, satisfacción)
- Recomendación metodológica: qué cambiar en la práctica
- Confianza (alta/media/baja)
- Evidencia: resúmenes de las lecciones que forman el patrón

LECCIONES A ANALIZAR ({total_lessons} lecciones de {total_projects} proyectos):
{lessons_text}"""


def detect_patterns(
    qdrant: QdrantClient,
    anthropic_client: anthropic.Anthropic,
    min_lessons: int = 20,
    category_filter: str | None = None
) -> list[dict]:
    """Detecta patrones recurrentes en el corpus de lecciones."""

    # Construir filtro opcional por categoría
    query_filter = None
    if category_filter:
        query_filter = Filter(must=[
            FieldCondition(
                key="category",
                match=MatchValue(value=category_filter)
            ),
            FieldCondition(
                key="validation_status",
                match=MatchValue(value="validated")
            )
        ])
    else:
        query_filter = Filter(must=[
            FieldCondition(
                key="validation_status",
                match=MatchValue(value="validated")
            )
        ])

    # Recuperar todas las lecciones validadas
    lessons = qdrant.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=query_filter,
        limit=500,
        with_vectors=False
    )[0]

    if len(lessons) < min_lessons:
        return [{
            "status": "insufficient_data",
            "message": f"Se necesitan al menos {min_lessons} lecciones. "
                       f"Actualmente hay {len(lessons)}."
        }]

    # Calcular estadísticas básicas antes de enviar al LLM
    project_types = Counter(l.payload["project_type"] for l in lessons)
    categories = Counter(l.payload["category"] for l in lessons)
    phases = Counter(l.payload["project_phase"] for l in lessons)

    # Preparar texto con lecciones agrupadas por categoría
    lessons_by_category = {}
    for lesson in lessons:
        cat = lesson.payload["category"]
        if cat not in lessons_by_category:
            lessons_by_category[cat] = []
        lessons_by_category[cat].append(lesson.payload)

    lessons_text = ""
    for cat, cat_lessons in lessons_by_category.items():
        lessons_text += f"\n### Categoría: {cat} ({len(cat_lessons)} lecciones)\n"
        for cl in cat_lessons:
            lessons_text += (
                f"- [{cl['polarity']}] {cl['summary']}\n"
                f"  Tipo proyecto: {cl['project_type']} | "
                f"Fase: {cl['project_phase']}\n"
                f"  Causa raíz: {cl['root_cause']}\n"
                f"  Impacto: {', '.join(cl['impact_areas'])}\n\n"
            )

    unique_projects = len(set(
        f"{l.payload['project_type']}_{l.payload['extraction_date'][:7]}"
        for l in lessons
    ))

    message = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": PATTERN_DETECTION_PROMPT.format(
                total_lessons=len(lessons),
                total_projects=unique_projects,
                lessons_text=lessons_text
            )
        }]
    )

    return parse_json_response(message.content[0].text)

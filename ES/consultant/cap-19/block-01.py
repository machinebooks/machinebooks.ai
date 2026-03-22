# Extraído de: LibroConsultor/cap-19-lecciones-aprendidas.md
EXTRACTION_PROMPT = """Analiza los siguientes documentos de un proyecto de consultoría
y extrae lecciones aprendidas candidatas.

CONTEXTO DEL PROYECTO:
- Tipo: {project_type}
- Cliente: {client_sector}
- Fase actual: {current_phase}
- Duración planificada: {planned_duration}
- Duración real hasta la fecha: {actual_duration}

CRITERIOS PARA UNA LECCIÓN VÁLIDA:
1. Debe ser TRANSFERIBLE a futuros proyectos (no específica de este cliente)
2. Debe tener CAUSA RAÍZ identificable (no solo "algo salió mal")
3. Debe incluir RECOMENDACIÓN CONCRETA (no solo "mejorar la comunicación")
4. Debe ser VERIFICABLE (basada en hechos del proyecto, no opiniones)

NO son lecciones:
- Observaciones puntuales sin patrón ("el cliente canceló la reunión del martes")
- Preferencias personales ("prefiero hacer las entrevistas por la mañana")
- Problemas ya conocidos y documentados en la metodología vigente

Para cada lección, devuelve un JSON con los campos:
summary, context, what_happened, root_cause, recommendation,
project_phase, category, impact_areas, polarity, confidence

DOCUMENTOS A ANALIZAR:
{documents}"""


def extract_lessons_from_project(
    project_docs: list[dict],
    project_metadata: dict
) -> list[LessonCandidate]:
    """Extrae lecciones candidatas de documentos de proyecto."""
    client = anthropic.Anthropic()

    # Concatenar documentos con separadores claros
    docs_text = "\n\n---DOCUMENTO---\n\n".join(
        f"[{doc['type']}] {doc['title']}\n"
        f"Fecha: {doc['date']}\n\n{doc['content']}"
        for doc in project_docs
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": EXTRACTION_PROMPT.format(
                project_type=project_metadata["type"],
                client_sector=project_metadata["sector"],
                current_phase=project_metadata["phase"],
                planned_duration=project_metadata["planned_duration"],
                actual_duration=project_metadata["actual_duration"],
                documents=docs_text
            )
        }]
    )

    # Parsear respuesta JSON y construir objetos LessonCandidate
    raw_lessons = parse_json_response(message.content[0].text)
    return [
        LessonCandidate(
            **lesson,
            project_type=project_metadata["type"],
            source_documents=[d["title"] for d in project_docs]
        )
        for lesson in raw_lessons
        if lesson.get("confidence", 0) >= 0.6  # Umbral de confianza
    ]

# Extraído de: LibroConsultor/cap-19-lecciones-aprendidas.md
from qdrant_client.models import Filter, FieldCondition, MatchValue

def find_relevant_lessons(
    project_context: dict,
    qdrant: QdrantClient,
    anthropic_client: anthropic.Anthropic,
    top_k: int = 5,
    min_score: float = 0.72
) -> list[dict]:
    """Busca lecciones relevantes para el contexto actual del proyecto."""

    # Construir query semántica desde el contexto del proyecto
    context_text = (
        f"Proyecto de {project_context['type']} para cliente del sector "
        f"{project_context['sector']}. "
        f"Fase actual: {project_context['phase']}. "
        f"Desafío actual: {project_context.get('current_challenge', '')}. "
        f"Equipo: {project_context.get('team_size', 'no especificado')} personas."
    )

    # Generar embedding de la consulta
    query_embedding = anthropic_client.embeddings.create(
        model="voyage-3",
        input=context_text
    ).data[0].embedding

    # Búsqueda semántica con filtros estructurales
    search_filter = Filter(must=[
        FieldCondition(
            key="validation_status",
            match=MatchValue(value="validated")
        )
    ])

    # Añadir filtro por tipo de proyecto si existe
    if project_context.get("type"):
        search_filter.must.append(
            FieldCondition(
                key="project_type",
                match=MatchValue(value=project_context["type"])
            )
        )

    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        query_filter=search_filter,
        limit=top_k * 2,  # Pedir el doble para filtrar por score
        score_threshold=min_score,
        with_payload=True
    )

    # Filtrar y enriquecer resultados
    relevant_lessons = []
    for result in results[:top_k]:
        lesson = result.payload
        lesson["relevance_score"] = round(result.score, 3)
        lesson["alert_text"] = generate_alert_text(
            lesson, project_context, anthropic_client
        )
        relevant_lessons.append(lesson)

        # Incrementar contador de veces mostrada
        qdrant.set_payload(
            collection_name=COLLECTION_NAME,
            payload={"times_surfaced": lesson["times_surfaced"] + 1},
            points=[result.id]
        )

    return relevant_lessons


def generate_alert_text(
    lesson: dict,
    project_context: dict,
    anthropic_client: anthropic.Anthropic
) -> str:
    """Genera texto de alerta contextualizado para el equipo."""
    message = anthropic_client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"""Redacta una alerta breve (3-4 frases) para un equipo
de consultoría que está en un proyecto de {project_context['type']}
en fase de {project_context['phase']}.

La lección aprendida relevante es:
- Resumen: {lesson['summary']}
- Contexto original: {lesson['context']}
- Recomendación: {lesson['recommendation']}

La alerta debe:
1. Explicar POR QUÉ es relevante para su proyecto actual
2. Incluir la recomendación concreta
3. Ser directa, sin preámbulos ni fórmulas de cortesía"""
        }]
    )
    return message.content[0].text

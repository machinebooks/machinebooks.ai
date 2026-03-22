# Extraído de: LibroConsultor/cap-26-caso-seguridad.md
def capture_lesson(
    project_id: str,
    control_id: str,
    context: str,
    decision: str,
    outcome: str,
    tags: list[str]
) -> None:
    """Captura una lección aprendida indexada por contexto."""

    # Generar embedding para búsqueda semántica futura
    embedding = generate_embedding(
        f"{context} | {decision} | {outcome}"
    )

    lesson = {
        "project_id": project_id,
        "control_id": control_id,
        "sector": "sector_publico",
        "framework": ["iso27001_2022", "ens_alta"],
        "context": context,
        "decision": decision,
        "outcome": outcome,
        "tags": tags,
        "date": "2025-11-28",
        "consultant": "senior_1"  # anonimizado
    }

    # Indexar en Qdrant para búsqueda semántica
    qdrant_client.upsert(
        collection_name="lessons_learned",
        points=[{
            "id": generate_uuid(),
            "vector": embedding,
            "payload": lesson
        }]
    )

# Extraído de: LibroConsultor/cap-03-consultor-potenciado.md
def prepare_client_engagement(
    client_ref: str,
    opportunity_description: str,
    meeting_date: str,
    attendees: list[dict]
) -> dict:
    """Flujo completo de preparación para un engagement con cliente."""

    results = {}

    # Paso 1: Briefing de reunión
    results["briefing"] = prepare_meeting_briefing(
        client_ref=client_ref,
        meeting_objective=f"Explorar oportunidad: {opportunity_description}",
        attendees=attendees
    )

    # Paso 2: Búsqueda de precedentes
    results["precedents"] = search_knowledge_base(
        query=opportunity_description,
        filters={"type": ["project", "proposal"]}
    )

    # Paso 3: Estimación preliminar
    historical = [
        p for p in results["precedents"]
        if p.get("type") == "project" and p.get("metrics")
    ]
    if len(historical) >= 2:
        results["estimation"] = estimate_project(
            description=opportunity_description,
            historical_projects=historical
        )
    else:
        results["estimation"] = {
            "warning": "Menos de 2 proyectos comparables. "
                       "Estimación no fiable — usar juicio experto.",
            "comparable_count": len(historical)
        }

    # Paso 4: Checklist pre-reunión
    results["checklist"] = {
        "briefing_reviewed": False,
        "estimation_validated": False,
        "questions_prepared": False,
        "materials_ready": False,
        "internal_alignment": False
    }

    return results

# Extraído de: LibroConsultor/cap-21-productizacion.md
from claude_agent_sdk import Agent, tool

@tool
def run_assessment(client_id: str, sector: str) -> dict:
    """Ejecuta el assessment completo para un cliente."""
    # 1. Recuperar respuestas del cuestionario (ya completado online)
    responses = get_client_responses(client_id)  # De la BD

    # 2. Evaluar cada dimensión
    dimensions = [
        "datos", "talento", "gobernanza",
        "infraestructura", "casos_uso", "cultura"
    ]
    result = AssessmentResult(client_id=client_id)

    for dim in dimensions:
        dim_responses = [r for r in responses if r["dimension"] == dim]

        # Detectar inconsistencias con Claude
        inconsistencies = detect_inconsistencies(dim, dim_responses)

        # Calcular puntuación (media ponderada de respuestas)
        raw_score = calculate_dimension_score(dim_responses)
        confidence = max(0.3, 1.0 - len(inconsistencies) * 0.15)

        result.dimensions.append(DimensionScore(
            dimension=dim,
            score=raw_score,
            confidence=confidence,
            inconsistencies=inconsistencies,
            evidence_gaps=find_evidence_gaps(dim_responses),
        ))

    result.calculate_overall()

    # 3. Generar informe ejecutivo
    report = generate_executive_report(
        result,
        client_name=get_client_name(client_id),
        sector=sector,
    )

    # 4. Guardar resultados y programar revisión de consultor
    save_assessment(client_id, result, report)
    schedule_consultant_review(client_id, result.flags_for_consultant)

    return {
        "overall_level": result.overall_level.name,
        "flags_count": len(result.flags_for_consultant),
        "report_generated": True,
        "consultant_review_scheduled": len(result.flags_for_consultant) > 0,
    }

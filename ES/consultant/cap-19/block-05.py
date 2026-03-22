# Extraído de: LibroConsultor/cap-19-lecciones-aprendidas.md
METHODOLOGY_UPDATE_PROMPT = """Eres un consultor de metodología para una
práctica de consultoría tecnológica. Analiza los siguientes patrones
detectados en lecciones aprendidas y genera recomendaciones concretas
de actualización metodológica.

PATRONES DETECTADOS:
{patterns}

METODOLOGÍA VIGENTE (secciones relevantes):
{current_methodology}

Para cada recomendación, indica:
1. Sección de la metodología afectada
2. Cambio propuesto (texto específico, no genérico)
3. Justificación con datos de los patrones
4. Riesgo de no implementar el cambio
5. Impacto estimado si se implementa
6. Prioridad (alta/media/baja)

NO recomiendes cambios genéricos tipo "mejorar la comunicación".
Cada cambio debe ser una instrucción específica que un director de
proyecto pueda implementar sin ambigüedad."""


def generate_methodology_recommendations(
    patterns: list[dict],
    methodology_sections: dict[str, str],
    anthropic_client: anthropic.Anthropic
) -> list[dict]:
    """Genera recomendaciones de actualización metodológica."""

    # Filtrar patrones con confianza alta o media
    relevant_patterns = [
        p for p in patterns
        if p.get("confidence") in ("alta", "media")
        and p.get("affected_projects", 0) >= 3
    ]

    if not relevant_patterns:
        return []

    patterns_text = "\n\n".join(
        f"PATRÓN {i+1}: {p['description']}\n"
        f"Proyectos afectados: {p['affected_projects']}\n"
        f"Causa raíz: {p['root_cause']}\n"
        f"Impacto agregado: {p['aggregated_impact']}\n"
        f"Confianza: {p['confidence']}"
        for i, p in enumerate(relevant_patterns)
    )

    methodology_text = "\n\n".join(
        f"## {section}\n{content}"
        for section, content in methodology_sections.items()
    )

    message = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": METHODOLOGY_UPDATE_PROMPT.format(
                patterns=patterns_text,
                current_methodology=methodology_text
            )
        }]
    )

    recommendations = parse_json_response(message.content[0].text)

    # Añadir metadata de trazabilidad
    for rec in recommendations:
        rec["generated_date"] = date.today().isoformat()
        rec["source_patterns"] = [p["description"] for p in relevant_patterns]
        rec["status"] = "pending_review"

    return recommendations

# Extraído de: LibroConsultor/cap-15-madurez-ia.md
def generate_maturity_roadmap(
    assessment: MaturityAssessment,
    benchmarks: list[BenchmarkComparison],
    client_constraints: dict  # presupuesto, plazos, recursos
) -> dict:
    """Genera roadmap de mejora basado en assessment y restricciones."""

    # Identificar la dimensión más débil como prioridad
    weakest = min(assessment.dimensions, key=lambda d: d.level)

    # Construir prompt con contexto completo
    roadmap_prompt = f"""Genera un roadmap de mejora de madurez IA para:

Organización: sector {assessment.sector}, {assessment.size_band} empleados
Nivel global: {assessment.overall_level_weighted}

Puntuaciones por dimensión:
{_format_dimension_scores(assessment.dimensions)}

Benchmarks sectoriales:
{_format_benchmarks(benchmarks)}

Restricciones del cliente:
- Presupuesto anual disponible para IA: {client_constraints.get('budget', 'No definido')}
- Perfiles técnicos de IA disponibles: {client_constraints.get('ai_headcount', 0)}
- Plazo regulatorio más próximo: {client_constraints.get('regulatory_deadline', 'Ninguno')}
- Apetito de riesgo: {client_constraints.get('risk_appetite', 'Moderado')}

Dimensión más débil: {weakest.dimension.value} ({weakest.level})
Gaps principales: {'; '.join(weakest.gaps)}

Genera un roadmap con tres horizontes:
1. Quick wins (0-3 meses): acciones de bajo coste y alto impacto
2. Consolidación (3-12 meses): construcción de capacidades
3. Transformación (12-24 meses): cambio estructural

Para cada acción incluye:
- Descripción concreta (qué hacer, no qué aspirar)
- Dimensión que mejora y estimación de impacto en nivel
- Dependencias (qué debe completarse antes)
- Rango de coste estimado (bajo/medio/alto)
- Perfil responsable sugerido

Prioriza: dimensiones más débiles primero, acciones sin coste antes
que las que requieren inversión, gobernanza antes que tecnología
(porque sin gobernanza los proyectos se estancan).

Incluye una sección de "NO hacer todavía" — acciones que el cliente
querrá hacer pero que requieren cimientos previos."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": roadmap_prompt}]
    )

    return _parse_roadmap(response.content[0].text)

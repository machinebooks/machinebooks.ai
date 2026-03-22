# Extraído de: LibroConsultor/cap-21-productizacion.md
from datetime import date

SECTOR_BENCHMARKS = {
    "financiero": {"datos": 3.8, "talento": 3.2, "gobernanza": 3.5,
                   "infraestructura": 3.6, "casos_uso": 3.1, "cultura": 2.8},
    "sector_publico": {"datos": 2.4, "talento": 2.1, "gobernanza": 2.8,
                       "infraestructura": 2.5, "casos_uso": 1.9, "cultura": 2.0},
    "industrial": {"datos": 2.9, "talento": 2.5, "gobernanza": 2.2,
                   "infraestructura": 3.0, "casos_uso": 2.6, "cultura": 2.3},
    "retail": {"datos": 3.2, "talento": 2.7, "gobernanza": 2.4,
               "infraestructura": 3.1, "casos_uso": 3.0, "cultura": 2.9},
}

def generate_executive_report(
    result: AssessmentResult,
    client_name: str,
    sector: str
) -> str:
    """Genera informe ejecutivo con benchmarks sectoriales."""
    benchmarks = SECTOR_BENCHMARKS.get(sector, {})

    # Construir comparativa por dimensión
    comparisons = []
    for dim in result.dimensions:
        bench = benchmarks.get(dim.dimension, 0)
        delta = dim.score - bench
        position = "por encima" if delta > 0.3 else (
            "por debajo" if delta < -0.3 else "en línea con"
        )
        comparisons.append(
            f"- **{dim.dimension.capitalize()}**: {dim.score:.1f}/5.0 "
            f"({position} la media del sector: {bench:.1f})"
        )

    comparisons_text = "\n".join(comparisons)

    # Generar narrativa con Claude
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=(
            "Eres un consultor senior especializado en adopción de IA. "
            "Genera un informe ejecutivo de assessment de madurez de IA. "
            "Tono: profesional, directo, orientado a la acción. "
            "Estructura: resumen ejecutivo (1 párrafo), hallazgos por "
            "dimensión (2-3 frases cada uno), top 3 recomendaciones "
            "priorizadas por impacto, y próximos pasos sugeridos. "
            "NO uses jerga vacía. Cada recomendación debe incluir "
            "una estimación de esfuerzo (bajo/medio/alto) y plazo."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Cliente: {client_name}\n"
                f"Sector: {sector}\n"
                f"Nivel global: {result.overall_level.name} "
                f"({result.overall_level.value}/5)\n"
                f"Fecha: {date.today().isoformat()}\n\n"
                f"Puntuaciones vs benchmark sectorial:\n"
                f"{comparisons_text}\n\n"
                f"Inconsistencias detectadas:\n"
                + ("\n".join(result.flags_for_consultant)
                   if result.flags_for_consultant
                   else "Ninguna detectada")
                + "\n\nGenera el informe ejecutivo."
            )
        }]
    )

    return message.content[0].text

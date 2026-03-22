# Extraído de: LibroConsultor/cap-15-madurez-ia.md
def generate_assessment_report(
    assessment: MaturityAssessment,
    benchmarks: list[BenchmarkComparison],
    roadmap: dict,
    consultant_notes: str  # Notas cualitativas del consultor
) -> str:
    """Genera el informe completo de assessment de madurez."""

    report_prompt = f"""Genera un informe ejecutivo de assessment de
madurez IA con la siguiente estructura:

## 1. Resumen ejecutivo (1 página)
- Nivel global y posición frente al sector
- Las 3 conclusiones principales
- La recomendación más urgente

## 2. Metodología
- Dimensiones evaluadas y pesos
- Stakeholders entrevistados ({assessment.stakeholders_interviewed})
- Fuentes de evidencia

## 3. Resultados por dimensión (1-2 páginas por dimensión)
{_format_dimension_details(assessment.dimensions, benchmarks)}

## 4. Análisis de gaps y prioridades
- Dimensiones bajo la mediana sectorial
- Interdependencias entre dimensiones
- Riesgos de no actuar

## 5. Roadmap de mejora
{_format_roadmap_summary(roadmap)}

## 6. Benchmarking sectorial
- Posición comparativa por dimensión
- Áreas de ventaja y desventaja relativa

## 7. Observaciones del consultor
{consultant_notes}

Tono: profesional pero directo. Datos antes que opiniones.
Sin jerga de consultoría vacía. Cada afirmación con evidencia.
Extensión total: 15-25 páginas."""

    response = client.messages.create(
        model="claude-opus-4-6",  # Opus para calidad de redacción
        max_tokens=8192,
        messages=[{"role": "user", "content": report_prompt}]
    )

    return response.content[0].text

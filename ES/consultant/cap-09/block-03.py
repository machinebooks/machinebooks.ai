# Extraído de: LibroConsultor/cap-09-generacion-propuestas.md
def evaluar_seccion(
    seccion: SeccionGenerada,
    contexto: ContextoPropuesta,
    criterio_relevante: dict
) -> dict:
    """Evalúa la calidad de una sección contra criterios del pliego."""

    prompt_evaluacion = f"""Evalúa esta sección de propuesta técnica como si fueras
el evaluador del organismo público que convoca el proyecto.

CRITERIO DE EVALUACIÓN:
- Nombre: {criterio_relevante['nombre']}
- Puntuación máxima: {criterio_relevante['puntuacion_maxima']} puntos
- Descripción: {criterio_relevante.get('descripcion', 'No especificada')}

SECCIÓN A EVALUAR:
{seccion.contenido}

REQUISITOS DEL PLIEGO RELEVANTES:
{chr(10).join(f'- {r["descripcion"]}' for r in contexto.requisitos_pliego[:15])}

Responde en JSON con esta estructura:
{{
    "puntuacion_estimada": <número de 0 a {criterio_relevante['puntuacion_maxima']}>,
    "fortalezas": ["lista de puntos fuertes"],
    "carencias": ["lista de carencias específicas"],
    "sugerencias_mejora": ["lista de mejoras concretas"],
    "especificidad": <1-10, cuánto se adapta al cliente específico>,
    "riesgo_generico": <true/false, si suena a plantilla reutilizada>
}}"""

    response = client_anthropic.messages.create(
        model="claude-haiku-4-5",  # Haiku para evaluación rápida
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt_evaluacion}]
    )

    import json
    evaluacion = json.loads(response.content[0].text)

    # Actualizar la sección con el score
    seccion.score_quality = (
        evaluacion["puntuacion_estimada"] /
        criterio_relevante["puntuacion_maxima"] * 100
    )

    return evaluacion

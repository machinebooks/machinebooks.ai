# Extraído de: LibroConsultor/cap-18-onboarding.md
def evaluate_scenario_response(
    scenario: Scenario,
    junior_response: str,
    junior_id: str
) -> dict:
    """Evalúa la respuesta del junior a un escenario simulado."""
    evaluation_prompt = f"""Evalúa la siguiente respuesta de un consultor junior
a un escenario de práctica.

ESCENARIO: {scenario.context}
TAREA: {scenario.task}
SOLUCIÓN DE REFERENCIA: {scenario.reference_solution}
ERRORES FRECUENTES A DETECTAR: {scenario.common_mistakes}

RESPUESTA DEL JUNIOR:
{junior_response}

Evalúa según estos criterios (cada uno de 0 a 10):
{chr(10).join(f"- {c['criterion']} (peso: {c['weight']})" for c in scenario.evaluation_criteria)}

Para cada criterio, proporciona:
1. Puntuación numérica (0-10)
2. Justificación de la puntuación en 2-3 frases
3. Un consejo específico de mejora

Al final, indica:
- Puntuación ponderada total (0-10)
- Calificación: "excelente" (>8), "aceptable" (6-8), "insuficiente" (<6)
- Los 2 puntos fuertes de la respuesta
- Los 2 puntos de mejora prioritarios
- Si detectas algún error frecuente de la lista, señálalo explícitamente
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system="Eres un evaluador de formación en consultoría. Evalúas con rigor "
               "pero con intención pedagógica. Nunca eres condescendiente. "
               "Señalas lo bueno y lo mejorable con la misma claridad.",
        messages=[{"role": "user", "content": evaluation_prompt}]
    )

    return {
        "scenario_id": scenario.scenario_id,
        "junior_id": junior_id,
        "evaluation": response.content[0].text,
        "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
        "timestamp": datetime.now().isoformat()
    }

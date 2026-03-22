# Extraído de: LibroCyberrange/cap-21-entrenar-soc.md
# Ejemplo didáctico: rúbrica de evaluación con Claude
# patrones/soc/evaluation/rubric_evaluator.py

import anthropic

client = anthropic.Anthropic()

RUBRIC_PROMPT = """Eres un evaluador experto de ejercicios
de entrenamiento SOC en un Cyber Range. Evalúa la respuesta
del analista según la rúbrica proporcionada.

INSTRUCCIONES:
- Sé específico en la justificación de cada puntuación
- Referencia acciones concretas del analista, no generalidades
- Si el analista cometió un error, explica por qué es un error
  y qué habría sido la acción correcta
- La evaluación debe ser formativa: el objetivo es que el
  analista aprenda, no que se sienta evaluado

ESCALA:
- 4 (Excelente): supera las expectativas del nivel
- 3 (Competente): cumple las expectativas
- 2 (En desarrollo): muestra comprensión parcial
- 1 (Insuficiente): no demuestra la competencia"""


def evaluate_with_rubric(
    scenario_id: str,
    analyst_actions: list[dict],
    scenario_ground_truth: dict,
    rubric: dict
) -> dict:
    """
    Evalúa el rendimiento del analista usando Claude como
    evaluador con una rúbrica estructurada.
    """
    evaluation_request = (
        f"ESCENARIO: {scenario_id}\n\n"
        f"ACCIONES DEL ANALISTA:\n"
        f"{json.dumps(analyst_actions, indent=2)}\n\n"
        f"VERDAD DEL TERRENO:\n"
        f"{json.dumps(scenario_ground_truth, indent=2)}\n\n"
        f"RÚBRICA DE EVALUACIÓN:\n"
        f"{json.dumps(rubric, indent=2)}\n\n"
        f"Evalúa cada criterio de la rúbrica con puntuación "
        f"y justificación detallada. Incluye recomendaciones "
        f"de mejora específicas para cada área."
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=RUBRIC_PROMPT,
        messages=[{
            "role": "user",
            "content": evaluation_request
        }]
    )

    return {
        "scenario_id": scenario_id,
        "evaluation": response.content[0].text,
        "model_used": "claude-sonnet-4-6",
        "rubric_version": rubric.get("version", "1.0")
    }


# Rúbrica para el escenario SOC-001 (agente que falla)
SOC_001_RUBRIC = {
    "version": "1.0",
    "criteria": [
        {
            "name": "deteccion_error_agente",
            "weight": 0.30,
            "description": "Capacidad de detectar que el agente "
                          "de IA ha clasificado incorrectamente "
                          "una alerta como falso positivo",
            "indicators": {
                "4": "Detecta el error en <15 min con proceso "
                     "sistemático de revisión de investigaciones",
                "3": "Detecta el error en <30 min revisando "
                     "alertas de mayor riesgo primero",
                "2": "Detecta el error en <60 min pero sin "
                     "proceso sistemático claro",
                "1": "No detecta el error o tarda >60 min"
            }
        },
        {
            "name": "respuesta_incidente",
            "weight": 0.25,
            "description": "Calidad de la respuesta una vez "
                          "identificado el ataque en curso",
            "indicators": {
                "4": "Contiene al atacante, preserva evidencia "
                     "forense y comunica el impacto correctamente",
                "3": "Contiene al atacante y preserva evidencia "
                     "pero la comunicación es incompleta",
                "2": "Contiene al atacante pero destruye "
                     "evidencia o no comunica",
                "1": "No contiene eficazmente al atacante"
            }
        },
        {
            "name": "propuesta_mejora_agente",
            "weight": 0.25,
            "description": "Calidad de la propuesta para mejorar "
                          "la lógica del agente de triaje",
            "indicators": {
                "4": "Identifica la causa raíz del error, "
                     "propone mejora específica y viable, "
                     "incluye métricas de validación",
                "3": "Identifica la causa raíz y propone "
                     "mejora viable",
                "2": "Propone mejora genérica sin análisis "
                     "de causa raíz",
                "1": "No propone mejora o la propuesta no "
                     "es viable"
            }
        },
        {
            "name": "pensamiento_critico_ia",
            "weight": 0.20,
            "description": "Demostración de pensamiento crítico "
                          "sobre las decisiones de la IA",
            "indicators": {
                "4": "Cuestiona sistemáticamente las decisiones "
                     "del agente, identifica patrones de error "
                     "y evalúa la confiabilidad del modelo",
                "3": "Revisa las decisiones del agente con "
                     "criterio pero sin proceso sistemático",
                "2": "Revisa solo cuando algo parece incorrecto",
                "1": "Confía en el agente sin revisión"
            }
        }
    ]
}

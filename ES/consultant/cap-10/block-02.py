# Extraído de: LibroConsultor/cap-10-estimacion-esfuerzos.md
import anthropic
import json

client = anthropic.Anthropic()

# Herramientas que el agente puede invocar
tools = [
    {
        "name": "buscar_proyectos_similares",
        "description": (
            "Busca proyectos históricos similares al proyecto descrito. "
            "Devuelve los N más similares con su score de similitud."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "descripcion_alcance": {
                    "type": "string",
                    "description": "Descripción del alcance del proyecto nuevo"
                },
                "tipo_servicio": {"type": "string"},
                "sector": {"type": "string"},
                "complejidad_regulatoria": {"type": "string"},
                "tecnologias": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "top_n": {
                    "type": "integer",
                    "description": "Número de proyectos similares a devolver"
                }
            },
            "required": [
                "descripcion_alcance", "tipo_servicio", "sector"
            ]
        }
    },
    {
        "name": "calcular_estimacion_calibrada",
        "description": (
            "Calcula estimación de esfuerzo calibrada a partir de "
            "proyectos similares y sus desviaciones históricas."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ids_proyectos_referencia": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "horas_estimadas_base": {
                    "type": "number",
                    "description": "Estimación base del consultor (horas)"
                },
                "nivel_confianza": {
                    "type": "number",
                    "description": "Nivel de confianza deseado (0.80, 0.90)"
                }
            },
            "required": [
                "ids_proyectos_referencia", "horas_estimadas_base"
            ]
        }
    }
]

SYSTEM_PROMPT = """Eres un agente de estimación de esfuerzos para proyectos
de consultoría tecnológica. Tu trabajo:

1. Recibir la descripción de un proyecto nuevo.
2. Buscar proyectos históricos similares en la base de datos.
3. Analizar las desviaciones históricas de esos proyectos.
4. Producir una estimación calibrada con intervalo de confianza.

Reglas:
- Siempre busca al menos 5 proyectos similares.
- Si encuentras menos de 3 con similitud > 0.6, marca como "baja confianza".
- Explica qué proyectos usaste como referencia y por qué.
- Incluye el ratio de desviación medio de los proyectos de referencia[^ratio_desviacion].
- Produce un rango (P10-P90), no un número puntual.
- Identifica los factores de riesgo específicos del proyecto nuevo
  que podrían aumentar la desviación."""

def ejecutar_estimacion(descripcion_proyecto: str) -> dict:
    """Ejecuta el agente de estimación sobre un proyecto nuevo."""
    messages = [
        {"role": "user", "content": descripcion_proyecto}
    ]
    # Bucle de agente: el modelo invoca herramientas iterativamente
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages
        )
        # Si el modelo termina sin invocar herramientas, devolvemos
        if response.stop_reason == "end_turn":
            return {
                "estimacion": response.content[0].text,
                "tokens_usados": response.usage.input_tokens
                    + response.usage.output_tokens
            }
        # Procesar invocaciones de herramientas
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                resultado = ejecutar_herramienta(
                    block.name, block.input
                )
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(resultado)
                })
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

# Extraído de: LibroCyberrange/cap-21-entrenar-soc.md
# Ejemplo didáctico: agente de investigación colaborativa
# patrones/soc/collaborative/investigation_agent.py

import anthropic

client = anthropic.Anthropic()

COLLABORATIVE_PROMPT = """Eres un agente de investigación SOC
trabajando junto a un analista humano en un Cyber Range.

TU ROL:
- Investigas alertas usando las herramientas disponibles
- Compartes tus hallazgos y razonamiento de forma transparente
- Pides contexto al analista cuando te falta información
  organizativa que no está en los logs
- Propones hipótesis y las validas con evidencia
- NUNCA tomas decisiones finales sin confirmación del analista

PROTOCOLO DE COLABORACIÓN:
1. Cuando encuentres un hallazgo relevante, compártelo
   inmediatamente con tu razonamiento
2. Si tienes múltiples hipótesis, preséntalas ordenadas
   por probabilidad con la evidencia de cada una
3. Cuando necesites contexto que no está en los datos
   técnicos (quién usa qué sistema, qué es normal en esta
   organización, historia previa de alertas similares),
   PREGUNTA al analista
4. Si el analista te corrige, ajusta tu investigación
5. Mantén un resumen actualizado de la investigación que
   incluya: hipótesis activas, evidencia a favor y en contra,
   y acciones pendientes

LIMITACIÓN DELIBERADA:
No tienes acceso al historial de tickets cerrados, ni al
directorio de empleados, ni al calendario de mantenimientos
programados. Esa información la tiene el analista."""


# Herramientas del agente colaborativo
collab_tools = [
    {
        "name": "query_siem",
        "description": "Consulta Elasticsearch para eventos de "
                       "seguridad. Soporta KQL y Lucene.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "index": {
                    "type": "string",
                    "description": "Índice: filebeat-*, "
                                   "winlogbeat-*, packetbeat-*"
                },
                "time_range": {"type": "string"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "query_edr",
        "description": "Consulta Wazuh para actividad en endpoints.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string"},
                "query_type": {
                    "type": "string",
                    "enum": ["syscheck", "syscollector",
                             "rootcheck", "active_response"]
                }
            },
            "required": ["agent_id", "query_type"]
        }
    },
    {
        "name": "ask_analyst",
        "description": "Pide información o contexto al analista "
                       "humano. Usa esto cuando necesites datos "
                       "que no están en los sistemas técnicos.",
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Pregunta concreta para el "
                                   "analista con contexto de "
                                   "por qué necesitas la info"
                }
            },
            "required": ["question"]
        }
    },
    {
        "name": "share_finding",
        "description": "Comparte un hallazgo con el analista "
                       "incluyendo evidencia y razonamiento.",
        "input_schema": {
            "type": "object",
            "properties": {
                "finding": {"type": "string"},
                "evidence": {"type": "string"},
                "confidence": {"type": "number"},
                "hypothesis": {"type": "string"}
            },
            "required": ["finding", "evidence"]
        }
    }
]


def run_collaborative_investigation(
    alert: dict,
    analyst_context: dict
) -> dict:
    """
    Ejecuta una investigación colaborativa entre el agente
    Claude y el analista humano. El agente investiga, comparte
    hallazgos y pide contexto. El analista proporciona
    información organizativa y toma decisiones finales.
    """
    messages = [{
        "role": "user",
        "content": (
            f"ALERTA PARA INVESTIGAR:\n"
            f"ID: {alert['id']}\n"
            f"Tipo: {alert['type']}\n"
            f"Servidor: {alert['hostname']}\n"
            f"Clasificación NIS-2: {alert['nis2_class']}\n"
            f"Descripción: {alert['description']}\n\n"
            f"El analista está disponible para responder "
            f"preguntas. Inicia la investigación."
        )
    }]

    investigation_timeline = []

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=COLLABORATIVE_PROMPT,
            tools=collab_tools,
            messages=messages
        )

        for block in response.content:
            if block.type == "tool_use":
                if block.name == "ask_analyst":
                    # La pregunta se muestra en la interfaz
                    # del Cyber Range. El analista responde
                    # en tiempo real.
                    investigation_timeline.append({
                        "type": "agent_asks_analyst",
                        "question": block.input["question"],
                        "timestamp": datetime.now().isoformat()
                    })
                    # La respuesta del analista se pasa al agente
                    analyst_response = get_analyst_response(
                        block.input["question"]
                    )
                    tool_result = analyst_response

                elif block.name == "share_finding":
                    investigation_timeline.append({
                        "type": "agent_shares_finding",
                        "finding": block.input,
                        "timestamp": datetime.now().isoformat()
                    })
                    tool_result = "Hallazgo recibido. Continúa."

                else:
                    # Herramientas técnicas (SIEM, EDR)
                    tool_result = execute_scenario_tool(
                        block.name, block.input
                    )
                    investigation_timeline.append({
                        "type": f"agent_uses_{block.name}",
                        "input": block.input,
                        "timestamp": datetime.now().isoformat()
                    })

                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(tool_result)
                    }]
                })

        if response.stop_reason == "end_turn":
            break

    return {
        "timeline": investigation_timeline,
        "duration_seconds": calculate_duration(
            investigation_timeline
        ),
        "agent_questions_asked": sum(
            1 for e in investigation_timeline
            if e["type"] == "agent_asks_analyst"
        )
    }

# Extraído de: LibroCyberrange/cap-20-soc-futuro.md
# Ejemplo didáctico: Agente SOC de triaje en el Cyber Range
# patrones/soc/triage_agent.py

import anthropic
from typing import Any

client = anthropic.Anthropic()

# Definición de herramientas disponibles para el agente SOC
tools = [
    {
        "name": "query_siem",
        "description": "Consulta el SIEM para buscar eventos de seguridad "
                       "correlacionados con una alerta. Acepta queries en "
                       "formato SPL o KQL.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Query de búsqueda en formato SPL"
                },
                "time_range": {
                    "type": "string",
                    "description": "Ventana temporal: '1h', '24h', '7d'"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "check_threat_intel",
        "description": "Verifica un indicador (IP, dominio, hash) contra "
                       "feeds de inteligencia de amenazas. Devuelve "
                       "reputación, campañas asociadas y referencias.",
        "input_schema": {
            "type": "object",
            "properties": {
                "indicator": {
                    "type": "string",
                    "description": "IoC a verificar: IP, dominio o hash"
                },
                "indicator_type": {
                    "type": "string",
                    "enum": ["ip", "domain", "hash_md5",
                             "hash_sha256", "url"]
                }
            },
            "required": ["indicator", "indicator_type"]
        }
    },
    {
        "name": "query_edr",
        "description": "Consulta el EDR para obtener información de "
                       "procesos, conexiones y actividad en un endpoint.",
        "input_schema": {
            "type": "object",
            "properties": {
                "hostname": {
                    "type": "string",
                    "description": "Nombre del host a investigar"
                },
                "query_type": {
                    "type": "string",
                    "enum": ["processes", "connections",
                             "file_changes", "registry"]
                },
                "time_range": {
                    "type": "string",
                    "description": "Ventana temporal de la consulta"
                }
            },
            "required": ["hostname", "query_type"]
        }
    },
    {
        "name": "classify_alert",
        "description": "Emite una clasificación final de la alerta con "
                       "nivel de confianza y justificación detallada.",
        "input_schema": {
            "type": "object",
            "properties": {
                "classification": {
                    "type": "string",
                    "enum": ["true_positive", "false_positive",
                             "suspicious", "escalate_to_human"]
                },
                "confidence": {
                    "type": "number",
                    "description": "Nivel de confianza entre 0.0 y 1.0"
                },
                "reasoning": {
                    "type": "string",
                    "description": "Justificación detallada de la "
                                   "clasificación con evidencia"
                },
                "recommended_action": {
                    "type": "string",
                    "description": "Acción recomendada: close, contain, "
                                   "investigate, escalate"
                }
            },
            "required": ["classification", "confidence",
                         "reasoning", "recommended_action"]
        }
    }
]

# System prompt del agente SOC Tier 0
SYSTEM_PROMPT = """Eres un agente de triaje SOC de Tier 0 en un Cyber Range
de entrenamiento. Tu función es investigar alertas de seguridad de forma
autónoma, consultando las herramientas disponibles para recopilar evidencia
antes de emitir una clasificación.

PROTOCOLO DE INVESTIGACIÓN:
1. Analiza la alerta recibida e identifica los indicadores clave.
2. Consulta el SIEM para buscar eventos correlacionados en la ventana
   temporal relevante.
3. Verifica los IoCs contra feeds de threat intelligence.
4. Si hay un endpoint afectado, consulta el EDR para actividad sospechosa.
5. Evalúa toda la evidencia recopilada antes de clasificar.
6. Si tu confianza es inferior a 0.75 o el riesgo potencial es alto,
   SIEMPRE escala a un analista humano.

REGLAS CRÍTICAS:
- Nunca clasifiques como falso positivo sin evidencia positiva de que la
  actividad es legítima. La ausencia de evidencia maliciosa NO es evidencia
  de legitimidad.
- Documenta todo tu razonamiento. Cada decisión debe ser auditable.
- Si detectas técnicas de MITRE ATT&CK, referéncialas por T-code.
- Prioriza la seguridad sobre la eficiencia: es mejor escalar una alerta
  benigna que cerrar una alerta maliciosa."""


def investigate_alert(alert: dict) -> dict:
    """
    Ejecuta una investigación completa de una alerta de seguridad.
    El agente usa las herramientas disponibles para recopilar evidencia
    y emitir una clasificación con trazabilidad completa.
    """
    messages = [{
        "role": "user",
        "content": (
            f"Investiga esta alerta de seguridad:\n\n"
            f"ID: {alert['id']}\n"
            f"Tipo: {alert['type']}\n"
            f"Severidad: {alert['severity']}\n"
            f"Origen: {alert['source']}\n"
            f"Timestamp: {alert['timestamp']}\n"
            f"Descripción: {alert['description']}\n"
            f"Indicadores: {alert.get('indicators', 'N/A')}\n\n"
            f"Usa las herramientas disponibles para investigar y "
            f"emite tu clasificación final."
        )
    }]

    # Bucle agéntico: el modelo decide qué herramientas usar
    investigation_log = []
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages
        )

        # Procesar cada bloque de la respuesta
        for block in response.content:
            if block.type == "tool_use":
                # Registrar la herramienta invocada
                investigation_log.append({
                    "tool": block.name,
                    "input": block.input,
                    "timestamp": "2026-03-21T10:15:00Z"
                })
                # En producción, aquí se ejecuta la herramienta
                # contra los sistemas reales del SOC.
                # En el Cyber Range, se ejecuta contra el
                # entorno simulado del escenario.
                tool_result = execute_tool(block.name, block.input)
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

        # Si el modelo terminó (stop_reason != tool_use), salir
        if response.stop_reason == "end_turn":
            break

    return {
        "alert_id": alert["id"],
        "investigation_log": investigation_log,
        "final_response": response.content,
        "steps_taken": len(investigation_log)
    }


def execute_tool(tool_name: str, tool_input: dict) -> Any:
    """
    Ejecuta una herramienta contra el entorno del Cyber Range.
    En el escenario de entrenamiento, estas herramientas devuelven
    datos simulados que reflejan el estado del ejercicio.
    """
    # Implementación específica por herramienta...
    # Los datos devueltos dependen del escenario activo
    pass

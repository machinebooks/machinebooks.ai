# Extraído de: LibroCyberrange/cap-04-claude-ecosistema.md
# Agente de red team automatizado con Claude Agent SDK
# Ejemplo didáctico: patrones/agentes/red_team_agent.py

import anthropic
import json

client = anthropic.Anthropic()

# Herramientas disponibles para el agente de red team
RED_TEAM_TOOLS = [
    {
        "name": "scan_network",
        "description": "Ejecuta un escaneo de red en la workzone del ejercicio",
        "input_schema": {
            "type": "object",
            "properties": {
                "target_range": {
                    "type": "string",
                    "description": "Rango CIDR a escanear (ej: 10.10.1.0/24)"
                },
                "scan_type": {
                    "type": "string",
                    "enum": ["quick", "service_detection", "vuln_scan"],
                    "description": "Tipo de escaneo"
                }
            },
            "required": ["target_range", "scan_type"]
        }
    },
    {
        "name": "attempt_exploit",
        "description": "Intenta explotar una vulnerabilidad específica en un host",
        "input_schema": {
            "type": "object",
            "properties": {
                "target_host": {"type": "string"},
                "target_port": {"type": "integer"},
                "exploit_type": {
                    "type": "string",
                    "description": "Tipo de exploit (ej: sql_injection, rce, lfi)"
                },
                "parameters": {
                    "type": "object",
                    "description": "Parámetros específicos del exploit"
                }
            },
            "required": ["target_host", "target_port", "exploit_type"]
        }
    },
    {
        "name": "check_flag",
        "description": "Verifica si se ha obtenido acceso a un flag del ejercicio",
        "input_schema": {
            "type": "object",
            "properties": {
                "target_host": {"type": "string"},
                "file_path": {"type": "string"}
            },
            "required": ["target_host", "file_path"]
        }
    },
    {
        "name": "log_technique",
        "description": "Registra una técnica MITRE ATT&CK utilizada",
        "input_schema": {
            "type": "object",
            "properties": {
                "technique_id": {"type": "string"},
                "description": {"type": "string"},
                "success": {"type": "boolean"}
            },
            "required": ["technique_id", "description", "success"]
        }
    }
]

RED_TEAM_SYSTEM = """Eres un agente de red team automatizado en un Cyber Range.
Tu objetivo es ejecutar una cadena de ataque contra la infraestructura del ejercicio
siguiendo la metodología MITRE ATT&CK.

REGLAS:
- Documenta CADA técnica utilizada con su ID MITRE ATT&CK.
- Sigue la kill chain: Reconnaissance → Initial Access → Execution →
  Persistence → Privilege Escalation → Lateral Movement → Exfiltration.
- Si un exploit falla, analiza el error y prueba una técnica alternativa.
- Máximo 20 iteraciones por ejercicio (previene loops infinitos).
- NUNCA intentes salir de la workzone asignada.
- Registra toda evidencia para el informe post-ejercicio.

CONTEXTO:
- Workzone: {workzone_id}
- Red asignada: {network_range}
- Objetivos conocidos: {known_targets}
- Tiempo límite: {time_limit_minutes} minutos
"""

async def run_red_team_agent(exercise_context: dict) -> dict:
    """Ejecuta el ciclo completo del agente de red team.

    Implementa el patrón ReAct: razona sobre la situación,
    ejecuta una acción (herramienta), observa el resultado,
    reflexiona y decide el siguiente paso.
    """
    messages = [{
        "role": "user",
        "content": (
            f"Inicia la cadena de ataque contra la infraestructura. "
            f"Red objetivo: {exercise_context['network_range']}. "
            f"Comienza con reconocimiento."
        )
    }]
    system = RED_TEAM_SYSTEM.format(**exercise_context)

    attack_log = []
    max_iterations = 20
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        response = client.messages.create(
            model="claude-sonnet-4-6",  # Sonnet: equilibrio razonamiento/coste
            max_tokens=2048,
            system=system,
            tools=RED_TEAM_TOOLS,
            messages=messages
        )

        # Si el agente decide que ha terminado
        if response.stop_reason == "end_turn":
            break

        # Si solicita usar una herramienta
        if response.stop_reason == "tool_use":
            tool_calls = [b for b in response.content if b.type == "tool_use"]
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for tool_call in tool_calls:
                # Ejecutar la herramienta en el sandbox de la workzone
                result = await execute_sandboxed_tool(
                    tool_name=tool_call.name,
                    arguments=tool_call.input,
                    workzone_id=exercise_context["workzone_id"]
                )
                attack_log.append({
                    "iteration": iteration,
                    "tool": tool_call.name,
                    "input": tool_call.input,
                    "result": result,
                })
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": json.dumps(result)
                })

            messages.append({"role": "user", "content": tool_results})

    return {
        "iterations": iteration,
        "attack_log": attack_log,
        "techniques_used": extract_techniques(attack_log),
        "flags_captured": extract_flags(attack_log),
    }

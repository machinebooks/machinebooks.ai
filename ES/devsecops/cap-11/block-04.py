# Extraído de: LibroDevSecOps/cap-11-remediacion-automatica.md
"""remediation_orchestrator.py — Orquestador de remediación."""
import anthropic
import json
from datetime import datetime

client = anthropic.Anthropic()

def remediate_finding(finding: dict) -> dict:
    """Procesa un hallazgo y genera PR de remediación."""
    # Construir contexto del hallazgo para el agente
    context = build_finding_context(finding)

    messages = [
        {
            "role": "user",
            "content": (
                f"Remedia el siguiente hallazgo de seguridad:\n\n"
                f"{json.dumps(context, indent=2, ensure_ascii=False)}\n\n"
                f"Sigue las reglas de operación. Empieza verificando "
                f"la política de exclusión, luego lee el código "
                f"afectado, y decide si generar auto_fix o advisory."
            )
        }
    ]

    # Bucle agentic: el agente llama herramientas hasta completar
    max_iterations = 15
    for _ in range(max_iterations):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=REMEDIATION_SYSTEM_PROMPT,
            tools=tools,
            messages=messages
        )

        # Procesar respuesta del modelo
        if response.stop_reason == "end_turn":
            # El agente terminó — extraer resultado
            return extract_result(response, finding)

        if response.stop_reason == "tool_use":
            # El agente quiere usar una herramienta
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(
                        block.name, block.input
                    )
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    })

            # Añadir respuesta del modelo y resultados
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            messages.append({
                "role": "user",
                "content": tool_results
            })

    return {
        "status": "max_iterations_reached",
        "finding_id": finding["id"]
    }


def execute_tool(name: str, params: dict) -> dict:
    """Ejecuta una herramienta y devuelve el resultado."""
    tool_map = {
        "read_file": read_file,
        "read_changelog": read_changelog,
        "create_branch": create_branch,
        "apply_fix": apply_fix,
        "create_pull_request": create_pull_request,
        "check_exclusion_policy": check_exclusion_policy,
    }
    fn = tool_map.get(name)
    if not fn:
        return {"error": f"Herramienta desconocida: {name}"}
    return fn(**params)

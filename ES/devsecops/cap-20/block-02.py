# Extraído de: LibroDevSecOps/cap-20-respuesta-incidentes.md
def run_incident_agent(incident: CorrelatedIncident) -> dict:
    """Ejecuta el agente de respuesta sobre un incidente correlado."""

    system_prompt = """Eres un agente de respuesta a incidentes de seguridad.
Tu rol es analizar incidentes, proponer acciones de contención y generar
documentación. REGLAS CRÍTICAS:
1. NUNCA ejecutes acciones destructivas sin request_human_approval previo.
2. Usa correlate_alerts para entender el alcance antes de proponer contención.
3. Consulta query_sbom para verificar si hay CVEs conocidas involucradas.
4. Documenta cada decisión con justificación técnica.
5. Si la severidad es CRITICAL, prioriza contención sobre análisis exhaustivo.
6. Genera el post-mortem al finalizar, incluyendo timeline y recomendaciones."""

    # Construir el mensaje inicial con el contexto del incidente
    incident_context = format_incident_for_agent(incident)

    messages = [
        {"role": "user", "content": (
            f"Se ha detectado un incidente de seguridad:\n\n"
            f"{incident_context}\n\n"
            f"Ejecuta el protocolo de respuesta completo: "
            f"analiza, propón contención, ejecuta con aprobación "
            f"y genera post-mortem."
        )}
    ]

    # Bucle agentic: el agente decide cuándo parar
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=system_prompt,
            tools=incident_tools,
            messages=messages
        )

        # Procesar la respuesta
        if response.stop_reason == "end_turn":
            # El agente ha terminado su análisis
            return extract_final_report(response, messages)

        if response.stop_reason == "tool_use":
            # Ejecutar los tools solicitados
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })

            # Añadir respuesta del agente y resultados al historial
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

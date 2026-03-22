# Extraído de: LibroFinOps/cap-05-tagging-cloud.md
def process_tool_call(tool_name: str, tool_input: dict) -> str:
    """Dispatcher de herramientas para el agente."""
    if tool_name == "list_untagged_ec2":
        result = list_untagged_ec2(**tool_input)
        return json.dumps(result)
    elif tool_name == "list_untagged_rds":
        # Implementación análoga para RDS
        return json.dumps([])
    elif tool_name == "propose_tag_correction":
        result = propose_tag_correction(**tool_input)
        return json.dumps(result)
    return json.dumps({"error": f"Herramienta desconocida: {tool_name}"})


def run_tag_audit_agent(region: str = "eu-west-1") -> str:
    """
    Ejecuta el agente de auditoría de tags.
    El agente analiza el inventario, infiere contexto y propone correcciones.
    Devuelve el informe final como texto.
    """
    required_tags = ["environment", "team", "service", "cost-center"]

    system_prompt = """Eres un agente de FinOps especializado en auditoría de etiquetas cloud.
Tu función es:
1. Listar los recursos EC2 y RDS sin etiquetas obligatorias en la región indicada.
2. Para cada recurso sin etiquetar, inferir los valores probables de las etiquetas
   basándote en el nombre del recurso, el VPC al que pertenece, las etiquetas parciales
   existentes y la fecha de creación.
3. Registrar propuestas de corrección con justificación clara y nivel de confianza honesto.
4. Generar un informe resumen con el número de recursos auditados, propuestas generadas
   y el impacto estimado en la atribución del gasto.

Importante:
- No ejecutes correcciones directamente. Solo propones.
- Si no tienes suficiente contexto para inferir un valor con confianza media o alta,
  indica confidence=low y explica qué información adicional necesitarías.
- Los valores de team deben ser uno de: backend, frontend, data, platform, security.
- Los valores de environment deben ser: prod, staging, dev, sandbox."""

    messages = [
        {
            "role": "user",
            "content": (
                f"Audita los recursos EC2 y RDS en la región {region}. "
                f"Etiquetas obligatorias: {', '.join(required_tags)}. "
                "Propón correcciones para todos los recursos sin etiquetar correctamente."
            ),
        }
    ]

    # Bucle agentic: el agente decide cuándo ha terminado
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=system_prompt,
            tools=TAG_AUDIT_TOOLS,
            messages=messages,
        )

        # Añadir respuesta del agente al histórico
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # El agente ha terminado. Extraer el texto final.
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "Auditoría completada sin informe textual."

        if response.stop_reason == "tool_use":
            # Procesar las herramientas solicitadas
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = process_tool_call(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            messages.append({"role": "user", "content": tool_results})

# Extraído de: LibroFinOps/cap-26-caso-cloud.md
def ejecutar_analisis_completo(self) -> list[Recomendacion]:
    """
    Ciclo completo: scanning → análisis → recomendaciones.
    Usa claude-sonnet-4-6: análisis de costes no requiere opus,
    pero sí mejor razonamiento que haiku para priorizar.
    Coste estimado por ejecución completa: $0,08-0,15.
    """
    system_prompt = """Eres un agente de optimización de costes AWS.

Objetivo: identificar waste y generar recomendaciones priorizadas.

Para cada recomendación:
1. Escanea los recursos con las herramientas disponibles
2. Analiza los datos para identificar ineficiencias
3. Cuantifica el ahorro potencial en dólares anuales
4. Asigna nivel de riesgo según reversibilidad e impacto
5. Describe la acción concreta con detalle suficiente

Reglas:
- Nunca ejecutes acciones: solo propones y recomiendas
- Incluye el razonamiento de por qué algo es waste
- Si hay incertidumbre, clasifica como riesgo ALTO
- Responde en español de España
- Devuelve recomendaciones en JSON estructurado"""

    messages = [{"role": "user", "content": (
        "Ejecuta análisis completo de la cuenta AWS. "
        "Escanea EC2, EBS y costes por servicio. "
        "Genera lista priorizada de recomendaciones."
    )}]

    # Agentic loop: el agente decide qué herramientas usar
    while True:
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=system_prompt,
            tools=self.tools,
            messages=messages,
        )

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    resultado = self._ejecutar_herramienta(
                        block.name, block.input
                    )
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(resultado, default=str),
                    })
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            return self._parsear_recomendaciones(response.content)
        else:
            break  # Stop reason inesperado

    return []

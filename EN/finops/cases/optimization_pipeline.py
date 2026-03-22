# Source: The FinOps Engineer and the Machine -- Chapter 26
# Pattern: Cloud optimization pipeline

def ejecutar_analisis_completo(self) -> list[Recomendacion]:
    """
    Full cycle: scanning → analysis → recommendations.
    Uses claude-sonnet-4-6: cost analysis doesn't require opus,
    but needs better reasoning than haiku for prioritization.
    Estimated cost per full execution: $0.08-0.15.
    """
    system_prompt = """You are an AWS cost optimization agent.

Objective: identify waste and generate prioritized recommendations.

For each recommendation:
1. Scan resources with the available tools
2. Analyze data to identify inefficiencies
3. Quantify potential savings in annual dollars
4. Assign risk level based on reversibility and impact
5. Describe the specific action with sufficient detail

Rules:
- Never execute actions: only propose and recommend
- Include reasoning for why something is waste
- If there is uncertainty, classify as HIGH risk
- Respond in European Spanish
- Return recommendations in structured JSON"""

    messages = [{"role": "user", "content": (
        "Execute full analysis of the AWS account. "
        "Scan EC2, EBS and costs by service. "
        "Generate prioritized list of recommendations."
    )}]

    # Agentic loop: the agent decides which tools to use
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
            break  # Unexpected stop reason

    return []

# Extraído de: LibroTecnico/cap-19-testing-ia.md
class AgentQualityEvaluator:
    """
    Evalúa la calidad de las trazas de ejecución de agentes.
    Se centra en eficiencia y corrección del proceso, no solo del resultado.
    """

    def evaluate_tool_selection(self, trace: AgentExecutionTrace, expected_tools: List[str]) -> dict:
        """
        Verifica que el agente usó las herramientas apropiadas.
        Un agente que usa 'search_documents' para una pregunta sobre configuración
        del sistema está tomando una decisión incorrecta aunque encuentre algo útil.
        """
        tools_used = [step["tool_used"] for step in trace.steps if step.get("tool_used")]

        # Herramientas usadas que no estaban esperadas
        unexpected_tools = set(tools_used) - set(expected_tools)
        # Herramientas esperadas que no se usaron
        missing_tools = set(expected_tools) - set(tools_used)

        return {
            "tools_used": tools_used,
            "unexpected_tools": list(unexpected_tools),
            "missing_tools": list(missing_tools),
            "tool_selection_correct": len(unexpected_tools) == 0 and len(missing_tools) == 0,
            "total_calls": trace.total_tool_calls,
        }


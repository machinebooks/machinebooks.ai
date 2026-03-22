# Extraído de: LibroTecnico/cap-19-testing-ia.md
    def evaluate_efficiency(
        self,
        trace: AgentExecutionTrace,
        max_expected_calls: int,
        max_tokens: int
    ) -> dict:
        """
        Evalúa la eficiencia de ejecución.
        Un agente que hace diez llamadas para responder una pregunta simple
        tiene un problema de razonamiento o de definición de herramientas.
        """
        return {
            "calls_within_limit": trace.total_tool_calls <= max_expected_calls,
            "tokens_within_limit": trace.total_tokens <= max_tokens,
            "calls_used": trace.total_tool_calls,
            "tokens_used": trace.total_tokens,
            "efficiency_ratio": max_expected_calls / max(trace.total_tool_calls, 1),
        }

    def evaluate_reasoning_consistency(self, trace: AgentExecutionTrace) -> dict:
        """
        Verifica que el razonamiento del agente es consistente entre pasos.
        Detecta si el agente recuperó información en un paso pero no la usó
        en pasos posteriores donde era relevante.
        """
        # Construir mapa de información recuperada por herramientas de búsqueda
        retrieved_info_steps = [
            i for i, step in enumerate(trace.steps)
            if step.get("tool_used") in ("search_documents", "get_portfolio_coverage")
            and step.get("output")
        ]

        # Verificar que los pasos de conclusión referencian la información recuperada
        conclusion_steps = [
            step for step in trace.steps
            if step.get("action") == "generate_conclusion"
        ]

        return {
            "info_retrieval_steps": len(retrieved_info_steps),
            "conclusion_steps": len(conclusion_steps),
            "has_unused_retrieval": len(retrieved_info_steps) > 0 and len(conclusion_steps) == 0,
        }



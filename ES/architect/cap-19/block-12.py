# Extraído de: LibroTecnico/cap-19-testing-ia.md
    def test_agent_does_not_exceed_call_budget(self, agent_runner):
        """
        Un análisis de oportunidad estándar no debe requerir más de 5 llamadas
        a herramientas. Si el agente necesita más, el razonamiento o las herramientas
        están mal definidos.
        """
        trace = agent_runner.execute(
            agent_slug="opportunity-analyzer",
            user_input="Analiza la oportunidad de migración cloud con presupuesto 200K",
            context={"opportunity_id": "opp-test-001"}
        )

        result = self.evaluator.evaluate_efficiency(
            trace=trace,
            max_expected_calls=5,
            max_tokens=4000
        )

        assert result["calls_within_limit"], \
            f"El agente hizo {result['calls_used']} llamadas (máximo esperado: 5). " \
            "Revisar definición de herramientas y prompt del sistema."

    def test_agent_reasoning_is_consistent(self, agent_runner):
        """
        El agente no debe recuperar información y luego ignorarla.
        Si busca propuestas similares, esa información debe influir en la conclusión.
        """
        trace = agent_runner.execute(
            agent_slug="opportunity-analyzer",
            user_input="Analiza la oportunidad de migración cloud con presupuesto 200K",
            context={"opportunity_id": "opp-test-001"}
        )

        result = self.evaluator.evaluate_reasoning_consistency(trace)

        assert not result["has_unused_retrieval"], \
            "El agente recuperó información pero no produjo ninguna conclusión. " \
            "Posible bucle en el razonamiento o herramienta de conclusión no invocada."

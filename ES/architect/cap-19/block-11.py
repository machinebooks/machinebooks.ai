# Extraído de: LibroTecnico/cap-19-testing-ia.md
class TestOpportunityAnalysisAgent:
    """
    Tests de calidad para el agente de análisis de oportunidades.
    Verifica que el razonamiento y la elección de herramientas son correctos.
    """

    evaluator = AgentQualityEvaluator()

    def test_agent_uses_correct_tools_for_opportunity_analysis(self, agent_runner):
        """
        Para un análisis de oportunidad, el agente debe usar:
        - search_documents (para buscar propuestas similares)
        - get_portfolio_coverage (para verificar capacidades)
        - calculate_relevance_score (para puntuar la oportunidad)
        NO debe usar herramientas de CRM o generación de propuesta en este flujo.
        """
        trace = agent_runner.execute(
            agent_slug="opportunity-analyzer",
            user_input="Analiza la oportunidad de migración cloud con presupuesto 200K",
            context={"opportunity_id": "opp-test-001"}
        )

        result = self.evaluator.evaluate_tool_selection(
            trace=trace,
            expected_tools=["search_documents", "get_portfolio_coverage", "calculate_relevance_score"]
        )

        assert result["tool_selection_correct"], \
            f"Herramientas inesperadas: {result['unexpected_tools']}. " \
            f"Herramientas faltantes: {result['missing_tools']}"


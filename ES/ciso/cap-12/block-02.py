# Extraído de: LibroCISO/cap-12-agentes-especializados.md
class RiskAgent(BaseAgent):
    """Agente especializado en gestión de riesgos.

    Calcula matrices, evalúa riesgo residual, identifica
    controles faltantes y propone planes de tratamiento.
    """

    TOOLS = [
        "query_risks",
        "calculate_risk_matrix",
        "evaluate_control_gap",
        "search_rag"
    ]

    def gather_data(self, params: dict) -> dict:
        """Recopila activos, amenazas, controles y metodología."""
        scope = params.get("scope", "full")

        # Obtener riesgos del alcance solicitado
        risks = self.tools.query_risks(
            filters=params.get("filters", {}),
            include_relations=["asset", "threat",
                             "vulnerability", "controls"]
        )

        # Obtener configuración de la metodología activa
        methodology = self.db_session.query(RiskMethodology)\
            .filter_by(is_active=True).first()

        # Calcular la matriz según la metodología
        matrix = self.tools.calculate_risk_matrix(
            methodology_id=methodology.id,
            risk_ids=[r["id"] for r in risks]
        )

        # Evaluar gaps de controles
        control_gaps = self.tools.evaluate_control_gap(
            risk_ids=[r["id"] for r in risks]
        )

        return {
            "risks": risks,
            "methodology": methodology.to_dict(),
            "matrix": matrix,
            "control_gaps": control_gaps
        }

    def analyze(self, gathered: dict, params: dict) -> dict:
        """Analiza riesgos con Claude y genera recomendaciones."""
        methodology_name = gathered["methodology"]["name"]

        system_prompt = (
            f"Eres un analista de riesgos experto en {methodology_name}. "
            f"Analiza la matriz de riesgos proporcionada.\n\n"
            "REGLAS:\n"
            "- Identifica los riesgos con nivel residual inaceptable\n"
            "- Para cada riesgo crítico, propón controles específicos\n"
            "- Prioriza por impacto × probabilidad\n"
            "- Señala controles existentes sin evidencia reciente\n"
            "- No inventes activos ni amenazas que no estén en los datos"
        )

        user_prompt = self._build_risk_prompt(gathered)

        response = self.llm_service.invoke(
            model="claude-sonnet-4-6",
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            max_tokens=4096,
            temperature=0.2
        )

        self.total_tokens += response.usage.total_tokens
        self.total_cost += response.cost

        return {
            "risk_analysis": response.content,
            "matrix_summary": gathered["matrix"],
            "critical_risks": self._extract_critical(
                gathered["risks"], gathered["matrix"]
            ),
            "model_used": response.model,
            "tokens": response.usage.total_tokens
        }

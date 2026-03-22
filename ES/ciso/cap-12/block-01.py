# Extraído de: LibroCISO/cap-12-agentes-especializados.md
class PrivacyAgent(BaseAgent):
    """Agente especializado en privacidad y protección de datos.

    Genera análisis RGPD, DPIAs, evaluaciones de tratamientos
    y recomendaciones de medidas técnicas y organizativas.
    """

    # Herramientas disponibles para este agente
    TOOLS = [
        "query_processings",
        "query_dpias",
        "query_breaches",
        "search_rag"
    ]

    def gather_data(self, params: dict) -> dict:
        """Consulta tratamiento, DPIAs previas y normativa aplicable."""
        processing_id = params["processing_id"]

        # Obtener datos del tratamiento desde BD
        processing = self.tools.query_processings(
            filters={"id": processing_id},
            include_relations=["data_categories", "legal_basis",
                             "recipients", "retention_periods"]
        )

        if not processing:
            raise ValueError(
                f"Tratamiento {processing_id} no encontrado"
            )

        # Buscar DPIAs previas para contexto
        previous_dpias = self.tools.query_dpias(
            filters={"processing_id": processing_id}
        )

        # Buscar brechas relacionadas (informan el análisis de riesgo)
        related_breaches = self.tools.query_breaches(
            filters={"processing_id": processing_id}
        )

        # Buscar normativa aplicable en el RAG
        rag_context = self.tools.search_rag(
            query=f"DPIA evaluación impacto tratamiento "
                  f"{processing['name']} {processing['purpose']}",
            collection="rgpd_lopdgdd",
            top_k=8
        )

        return {
            "processing": processing,
            "previous_dpias": previous_dpias,
            "related_breaches": related_breaches,
            "normative_context": rag_context
        }

    def analyze(self, gathered: dict, params: dict) -> dict:
        """Analiza el tratamiento con Claude aplicando criterios RGPD."""
        processing = gathered["processing"]

        system_prompt = (
            "Eres un analista de privacidad experto en RGPD y LOPDGDD. "
            "Analiza el tratamiento proporcionado siguiendo los "
            "criterios de la AEPD para evaluaciones de impacto.\n\n"
            "REGLAS:\n"
            "- Cita artículos específicos del RGPD cuando apliquen\n"
            "- Si falta información, indícalo explícitamente\n"
            "- No inventes datos que no estén en el contexto\n"
            "- Evalúa necesidad, proporcionalidad y riesgos\n"
            "- Propón medidas técnicas y organizativas concretas"
        )

        user_prompt = self._build_analysis_prompt(gathered)

        # Llamada al LLM con tracking de tokens
        response = self.llm_service.invoke(
            model="claude-sonnet-4-6",
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            max_tokens=4096,
            temperature=0.2  # Baja: queremos precisión, no creatividad
        )

        # Actualizar contadores para tracing
        self.total_tokens += response.usage.total_tokens
        self.total_cost += response.cost

        return {
            "analysis_text": response.content,
            "model_used": response.model,
            "tokens": response.usage.total_tokens,
            "cost": response.cost
        }

    def generate_output(self, analysis: dict,
                        params: dict) -> dict:
        """Genera el artefacto formal: informe de análisis RGPD."""
        output_format = params.get("output_format", "structured")

        output = {
            "type": "privacy_analysis",
            "processing_id": params["processing_id"],
            "analysis": analysis["analysis_text"],
            "model_used": analysis["model_used"],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "requires_dpia": self._extract_dpia_necessity(
                analysis["analysis_text"]
            ),
            "recommended_measures": self._extract_measures(
                analysis["analysis_text"]
            ),
            "status": "draft"  # Siempre draft, el CISO aprueba
        }

        return output

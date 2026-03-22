# Extraído de: LibroTecnico/cap-19-testing-ia.md
    def evaluate(
        self,
        prompt: str,
        response: str,
        context: Optional[str] = None,
        service_category: str = "rag_services",
    ) -> dict:
        """
        Evalúa un output y devuelve métricas + análisis de conformidad
        con el perfil de calidad de la categoría.
        """
        context_text = context or "Sin contexto adicional (generación directa)"

        eval_prompt = self.EVALUATION_PROMPT.format(
            context=context_text[:3000],  # Limitar para no exceder ventana
            prompt=prompt[:1000],
            response=response[:2000],
        )

        # Llamada al evaluador: claude-haiku-4-5 por coste y velocidad
        message = self.client.messages.create(
            model=self.EVALUATOR_MODEL,
            max_tokens=512,
            messages=[{"role": "user", "content": eval_prompt}],
        )

        # En producción, un evaluador que falla no debe bloquear el flujo principal
        raw_scores = json.loads(message.content[0].text)
        profile = QUALITY_PROFILES.get(service_category, QUALITY_PROFILES["rag_services"])

        # Determinar conformidad por métrica
        conformance = self._check_conformance(raw_scores, profile)

        return {
            "scores": raw_scores,
            "profile": service_category,
            "conformance": conformance,
            "overall_pass": all(conformance.values()),
            "tokens_used": message.usage.input_tokens + message.usage.output_tokens,
        }

    def _check_conformance(self, scores: dict, profile: QualityProfile) -> dict:
        """Verifica si cada métrica supera (o no supera) su umbral."""
        return {
            "hallucination": scores["hallucination_score"] <= profile.hallucination_threshold,
            "groundedness": scores["groundedness_score"] >= profile.groundedness_threshold,
            "relevance": scores["relevance_score"] >= profile.relevance_threshold,
            "coherence": scores["coherence_score"] >= profile.coherence_threshold,
            "bias": scores["bias_score"] <= profile.bias_threshold,
            "toxicity": scores["toxicity_score"] <= profile.toxicity_threshold,
            "pii": scores["pii_score"] <= profile.pii_threshold,
        }

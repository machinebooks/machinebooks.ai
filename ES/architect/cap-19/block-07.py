# Extraído de: LibroTecnico/cap-19-testing-ia.md
        # Evaluar con Quality Scorer
        evaluation = self.scorer.evaluate(
            prompt="Analiza el documento de requisitos...",
            response=output,
            context=self.TEST_DOCUMENT,
            service_category="analysis",
        )

        profile = QUALITY_PROFILES["analysis"]

        # Verificar que se cumplen los umbrales del perfil
        assert evaluation["scores"]["hallucination_score"] <= profile.hallucination_threshold, \
            f"Hallucination score {evaluation['scores']['hallucination_score']:.2f} " \
            f"excede umbral {profile.hallucination_threshold}"

        assert evaluation["scores"]["groundedness_score"] >= profile.groundedness_threshold, \
            f"Groundedness score {evaluation['scores']['groundedness_score']:.2f} " \
            f"por debajo del umbral {profile.groundedness_threshold}"

        assert evaluation["scores"]["coherence_score"] >= profile.coherence_threshold, \
            f"Coherence score {evaluation['scores']['coherence_score']:.2f} " \
            f"por debajo del umbral {profile.coherence_threshold}"

        # Verificar estructura del output (semántica, no literal)
        assert any(term in output.lower() for term in ["go", "no-go", "recomendación"]), \
            "El output no contiene una recomendación explícita"

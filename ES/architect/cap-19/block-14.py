# Extraído de: LibroTecnico/cap-19-testing-ia.md
    def detect_quality_regression(
        self,
        service_type: str,
        baseline_days: int = 7,
        comparison_days: int = 1,
        regression_threshold: float = 0.15,
        db_session=None,
    ) -> dict:
        """
        Detecta regresiones de calidad comparando el período actual
        con la baseline histórica. Un cambio de >15% en cualquier
        métrica crítica dispara una alerta.
        """
        # Período de baseline: semana anterior
        baseline_cutoff = datetime.utcnow() - timedelta(days=baseline_days + comparison_days)
        comparison_cutoff = datetime.utcnow() - timedelta(days=comparison_days)

        def get_avg_metrics(start, end):
            return db_session.query(
                func.avg(LLMQualityScore.hallucination_score),
                func.avg(LLMQualityScore.groundedness_score),
                func.avg(LLMQualityScore.coherence_score),
            ).join(LLMUsageLog).filter(
                LLMUsageLog.service_type == service_type,
                LLMQualityScore.created_at.between(start, end),
            ).first()

        baseline = get_avg_metrics(baseline_cutoff, comparison_cutoff)
        current = get_avg_metrics(comparison_cutoff, datetime.utcnow())

        regressions = []

        # Verificar regresión en hallucination (subida = peor)
        if baseline[0] and current[0]:
            change = (float(current[0]) - float(baseline[0])) / max(float(baseline[0]), 0.001)
            if change > regression_threshold:
                regressions.append({
                    "metric": "hallucination_score",
                    "baseline": round(float(baseline[0]), 3),
                    "current": round(float(current[0]), 3),
                    "change_pct": round(change * 100, 1),
                    "direction": "increase",
                    "severity": "high" if change > 0.30 else "medium",
                })


# Extraído de: LibroTecnico/cap-19-testing-ia.md
    def calculate_human_auto_correlation(
        self,
        service_type: str,
        days: int = 30,
        db_session=None,
    ) -> dict:
        """
        Calcula la correlación entre el score automático agregado
        y el rating humano para el período indicado.
        Una correlación < 0.65 indica desviación del evaluador automático.
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Solo interacciones que tienen rating humano
        results = db_session.query(
            LLMQualityScore.overall_score,
            LLMQualityScore.human_rating,
        ).join(LLMUsageLog).filter(
            LLMUsageLog.service_type == service_type,
            LLMQualityScore.human_rating.isnot(None),
            LLMQualityScore.created_at >= cutoff,
        ).all()

        if len(results) < 30:
            return {
                "service": service_type,
                "correlation": None,
                "sample_size": len(results),
                "warning": "Muestra insuficiente para calibración (mínimo 30 interacciones con rating humano)",
            }

        # Cálculo de correlación de Pearson
        # Implementación manual para evitar dependencia; en producción, usar scipy.stats.pearsonr
        auto_scores = [float(r.overall_score) for r in results]
        human_scores = [float(r.human_rating) / 5.0 for r in results]  # Normalizar 1-5 a 0-1

        n = len(auto_scores)
        mean_auto = sum(auto_scores) / n
        mean_human = sum(human_scores) / n

        numerator = sum((a - mean_auto) * (h - mean_human) for a, h in zip(auto_scores, human_scores))
        denom_auto = sum((a - mean_auto) ** 2 for a in auto_scores) ** 0.5
        denom_human = sum((h - mean_human) ** 2 for h in human_scores) ** 0.5

        correlation = numerator / (denom_auto * denom_human) if denom_auto * denom_human > 0 else 0.0

        return {
            "service": service_type,
            "correlation": round(correlation, 3),
            "sample_size": n,
            "calibration_needed": correlation < 0.65,
            "period_days": days,
        }

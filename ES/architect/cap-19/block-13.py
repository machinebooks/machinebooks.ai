# Extraído de: LibroTecnico/cap-19-testing-ia.md
from sqlalchemy import func
from models.llm_quality_score import LLMQualityScore
from models.llm_usage_log import LLMUsageLog
from datetime import datetime, timedelta


class QualityFeedbackAnalyzer:
    """
    Analiza el feedback loop de calidad para detectar degradaciones
    y calcular la correlación entre evaluación automática y humana.
    """

    def get_service_quality_trend(
        self,
        service_type: str,
        days: int = 7,
        db_session=None
    ) -> dict:
        """
        Devuelve la tendencia de calidad para un servicio en los últimos N días.
        Agrupa por día para detectar cambios bruscos (indicativos de
        cambios de modelo o de prompt).
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Join con LLMUsageLog para filtrar por servicio
        results = db_session.query(
            func.date(LLMQualityScore.created_at).label("date"),
            func.avg(LLMQualityScore.hallucination_score).label("avg_hallucination"),
            func.avg(LLMQualityScore.groundedness_score).label("avg_groundedness"),
            func.avg(LLMQualityScore.relevance_score).label("avg_relevance"),
            func.avg(LLMQualityScore.coherence_score).label("avg_coherence"),
            func.count(LLMQualityScore.id).label("total_evaluations"),
        ).join(
            LLMUsageLog, LLMQualityScore.usage_log_id == LLMUsageLog.id
        ).filter(
            LLMUsageLog.service_type == service_type,
            LLMQualityScore.created_at >= cutoff,
        ).group_by(
            func.date(LLMQualityScore.created_at)
        ).order_by("date").all()

        return {
            "service": service_type,
            "period_days": days,
            "daily_metrics": [
                {
                    "date": str(r.date),
                    "avg_hallucination": round(float(r.avg_hallucination or 0), 3),
                    "avg_groundedness": round(float(r.avg_groundedness or 0), 3),
                    "avg_relevance": round(float(r.avg_relevance or 0), 3),
                    "avg_coherence": round(float(r.avg_coherence or 0), 3),
                    "total_evaluations": r.total_evaluations,
                }
                for r in results
            ],
        }


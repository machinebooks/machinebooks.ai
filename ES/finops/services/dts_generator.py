# Extraído de: LibroFinOps/cap-21-aiact-auditoria.md
# services/dts_generator.py
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from models.llm_audit import LLMUsageLog, LLMQualityScore


class DTSGenerator:
    """
    Genera el borrador de la Documentación Técnica del Sistema
    según el Artículo 11 del AI Act. Consolida información del
    tracking, policies y logs de incidentes.
    """

    def generate_dts_summary(self, db: Session, system_name: str, version: str) -> dict:
        one_year_ago = datetime.utcnow() - timedelta(days=365)

        total = db.query(func.count(LLMUsageLog.id)).filter(
            LLMUsageLog.created_at >= one_year_ago
        ).scalar()
        decision_count = db.query(func.count(LLMUsageLog.id)).filter(
            LLMUsageLog.created_at >= one_year_ago,
            LLMUsageLog.decision_relevant == True,
        ).scalar()
        avg_quality = db.query(func.avg(LLMQualityScore.score)).join(
            LLMUsageLog
        ).filter(LLMUsageLog.created_at >= one_year_ago).scalar()

        return {
            "document_type": "AI_Act_Technical_Documentation_Summary",
            "system_name": system_name,
            "version": version,
            "generated_at": datetime.utcnow().isoformat(),
            "article_11_sections": {
                "a_general_description": {
                    "purpose": f"Asistencia a decisiones con IA para {system_name}",
                    "risk_category": "medium",
                },
                "b_design": {
                    "architecture": "FastAPI + Claude Agent SDK + LLMUsageLog",
                    "models": "claude-sonnet-4-6, claude-haiku-4-5",
                },
                "c_performance": {
                    "total_interactions_12m": total,
                    "decision_relevant_12m": decision_count,
                    "avg_quality_score": round(float(avg_quality or 0), 3),
                },
                "d_human_oversight": {
                    "mechanism": "Revisión y aprobación explícita del usuario",
                    "override": "El usuario puede rechazar cualquier salida",
                },
            },
        }

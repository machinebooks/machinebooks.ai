# Extraído de: LibroCISO/cap-21-celery-async.md
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from celery.utils.log import get_task_logger
from datetime import datetime

logger = get_task_logger(__name__)

@shared_task(
    bind=True,  # Acceso a self para actualizar estado
    name="app.tasks.ai.run_risk_analysis",
    queue="ai",
    soft_time_limit=300,   # 5 minutos: excepción controlada
    time_limit=360,        # 6 minutos: kill del proceso
    max_retries=2,         # Reintentar hasta 2 veces si falla
    retry_backoff=30,      # 30 segundos entre reintentos
    retry_jitter=True,     # Añadir variación aleatoria al backoff
    acks_late=True,        # Confirmar solo tras completar (no al recibir)
)
def run_risk_analysis(self, analysis_id: int, user_id: int,
                      tenant_id: int, asset_ids: list[int],
                      methodology: str = "MAGERIT"):
    """
    Ejecuta un análisis de riesgos con agente de IA.
    Actualiza el progreso en la BD para que el frontend lo muestre.
    """
    from app.models import RiskAnalysis, AnalysisStatus
    from app.services.ai.risk_agent import RiskAgent
    from app.database import get_session

    session = get_session()
    analysis = session.get(RiskAnalysis, analysis_id)

    try:
        # Fase 1: Preparación — inicializar estado y agente (10%)
        analysis.status = AnalysisStatus.RUNNING
        analysis.progress = 10
        analysis.started_at = datetime.utcnow()
        session.commit()

        self.update_state(
            state="PROGRESS",
            meta={"progress": 10, "phase": "Preparando activos"}
        )

        agent = RiskAgent(tenant_id=tenant_id, methodology=methodology)
        assets = agent.load_assets(asset_ids)

        # Fase 2-3: Análisis con LLM (20-80%)
        # Cada activo se analiza individualmente con el agente de riesgo.
        # Las fases intermedias (carga de amenazas, consolidación parcial)
        # siguen el mismo patrón de update_state.
        total_assets = len(assets)
        for i, asset in enumerate(assets):
            result = agent.analyze_asset(asset)
            agent.save_partial_result(analysis_id, asset.id, result)

            # Progreso proporcional entre 20% y 80%
            progress = 20 + int((i + 1) / total_assets * 60)
            analysis.progress = progress
            session.commit()

            self.update_state(
                state="PROGRESS",
                meta={
                    "progress": progress,
                    "phase": f"Activo {i+1}/{total_assets}: {asset.name}"
                }
            )

        # Fase 4-5: Consolidación, recomendaciones y cierre (80-100%)
        # Las fases intermedias siguen el mismo patrón de update_state
        recommendations = agent.generate_recommendations(analysis_id)
        analysis.status = AnalysisStatus.COMPLETED
        analysis.progress = 100
        analysis.completed_at = datetime.utcnow()
        analysis.duration_seconds = (
            analysis.completed_at - analysis.started_at
        ).total_seconds()
        analysis.ai_cost_tokens = agent.total_tokens_used
        analysis.ai_cost_usd = agent.total_cost_usd
        session.commit()

        logger.info(
            "Análisis completado",
            extra={
                "analysis_id": analysis_id,
                "assets_count": total_assets,
                "duration_s": analysis.duration_seconds,
                "tokens": agent.total_tokens_used,
            }
        )

        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "assets_analyzed": total_assets,
            "duration_seconds": analysis.duration_seconds,
        }

    except SoftTimeLimitExceeded:
        # Timeout controlado: guardar resultados parciales
        logger.warning(
            "Análisis excedió soft limit de 300s",
            extra={"analysis_id": analysis_id}
        )
        analysis.status = AnalysisStatus.TIMEOUT
        analysis.completed_at = datetime.utcnow()
        analysis.error_message = (
            "El análisis excedió el tiempo máximo de 5 minutos. "
            "Los resultados parciales se han guardado."
        )
        session.commit()
        # NO reintentar en timeout — los resultados parciales ya están guardados
        return {
            "analysis_id": analysis_id,
            "status": "timeout",
            "partial_results": True,
        }

    except Exception as exc:
        logger.error(
            "Error en análisis de riesgos",
            extra={"analysis_id": analysis_id, "error": str(exc)}
        )
        analysis.status = AnalysisStatus.FAILED
        analysis.error_message = str(exc)[:500]
        session.commit()
        # Reintentar si es un error transitorio (red, LLM)
        raise self.retry(exc=exc)

# Extraído de: LibroPQC/cap-26-criptografo-futuro.md
from celery import shared_task
from celery.schedules import crontab
from app.agent.crypto_monitor_agent import run_monitoring_cycle
from app.models import Organization, MonitoringLog
from app.extensions import db
import logging

logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    name="crypto_monitoring.continuous_scan",
    max_retries=2,
    soft_time_limit=600,   # 10 minutos por organización
    rate_limit="5/h"       # Máximo 5 ejecuciones por hora
)
def continuous_crypto_scan(self, organization_id: int):
    """Monitorización continua del estado criptográfico de una organización."""
    try:
        org = Organization.query.get(organization_id)
        if not org or not org.is_active:
            return {"status": "skipped", "reason": "org_inactive"}

        # Obtener último ciclo completado
        last_log = MonitoringLog.query.filter_by(
            organization_id=organization_id,
            status="completed"
        ).order_by(MonitoringLog.completed_at.desc()).first()

        last_check = last_log.completed_at.isoformat() if last_log else None

        # Ejecutar ciclo de monitorización
        result = run_monitoring_cycle(
            organization_id=organization_id,
            repos=[r.id for r in org.repositories if r.monitoring_enabled],
            cloud_accounts=[c.id for c in org.cloud_accounts if c.monitoring_enabled],
            last_check=last_check
        )

        # Registrar resultado
        log = MonitoringLog(
            organization_id=organization_id,
            status="completed",
            findings_count=result["findings_updated"],
            iterations=result["iterations"],
            summary=result["summary"]
        )
        db.session.add(log)
        db.session.commit()

        logger.info(
            f"Monitoring cycle completed for org {organization_id}: "
            f"{result['findings_updated']} findings updated"
        )
        return result

    except Exception as e:
        logger.error(f"Monitoring failed for org {organization_id}: {e}")
        raise self.retry(exc=e, countdown=300)


# Configuración de Celery Beat para monitorización programada
# Se añade al diccionario beat_schedule en celery_app.py
MONITORING_SCHEDULE = {
    "crypto-monitoring-daily": {
        "task": "crypto_monitoring.continuous_scan",
        "schedule": crontab(hour=2, minute=0),  # 02:00 cada día
        "kwargs": {"organization_id": None},     # Se itera sobre orgs activas
        "options": {"queue": "monitoring"}
    }
}

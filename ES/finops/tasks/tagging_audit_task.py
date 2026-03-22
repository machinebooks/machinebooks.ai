# Extraído de: LibroFinOps/cap-05-tagging-cloud.md
# tasks/tagging_audit_task.py
from celery import shared_task
from .agents.tag_audit_agent import run_tag_audit_agent
import logging

logger = logging.getLogger(__name__)

@shared_task(name="weekly_tag_audit")
def weekly_tag_audit():
    """
    Auditoría semanal de etiquetas. Ejecuta el agente Claude
    para identificar recursos sin etiquetar y proponer correcciones.
    Se ejecuta cada lunes a las 08:00 vía Celery Beat.
    """
    regions = ["eu-west-1", "us-east-1"]  # Regiones activas del proyecto

    for region in regions:
        try:
            logger.info(f"Iniciando auditoría de tags en {region}")
            report = run_tag_audit_agent(region=region)
            logger.info(f"Auditoría completada para {region}: {report[:200]}...")
            # En producción: enviar el informe al canal de Slack del equipo de FinOps
            # notify_finops_channel(f"Auditoría de tags {region}:\n{report}")
        except Exception as exc:
            logger.error(f"Error en auditoría de tags ({region}): {exc}")

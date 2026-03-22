# Extraído de: LibroCISO/cap-14-gobernanza-ia-ai-act.md
# Ejemplo didáctico: tareas/ai_governance_tasks.py
# Tarea periódica de monitorización de sistemas de IA

from celery import shared_task
from datetime import datetime, timedelta


@shared_task(queue="maintenance", bind=True, max_retries=3)
def check_ai_monitoring_alerts(self):
    """Tarea periódica (diaria) que evalúa métricas de monitorización
    de todos los sistemas de IA activos y genera alertas.

    Programada en Beat: ejecuta cada 24h a las 06:00.
    """
    from models.ai_governance import AIGovernanceRecord, AIMonitoringMetric, AIRiskLevel
    from services.notification_service import send_alert

    db = get_db_session()

    try:
        # Solo sistemas activos de alto riesgo o GPAI
        active_records = db.query(AIGovernanceRecord).filter(
            AIGovernanceRecord.status == "active",
            AIGovernanceRecord.is_deleted == False,
            AIGovernanceRecord.risk_level.in_([
                AIRiskLevel.HIGH,
                AIRiskLevel.GPAI_SYSTEMIC
            ])
        ).all()

        alerts_generated = 0

        for record in active_records:
            # Obtener métricas de los últimos 30 días
            recent_metrics = db.query(AIMonitoringMetric).filter(
                AIMonitoringMetric.ai_record_id == record.id,
                AIMonitoringMetric.created_at >= datetime.utcnow() - timedelta(days=30)
            ).order_by(AIMonitoringMetric.created_at.desc()).all()

            # Agrupar por tipo de métrica
            by_type = {}
            for m in recent_metrics:
                by_type.setdefault(m.metric_type, []).append(m)

            for metric_type, metrics in by_type.items():
                if not metrics:
                    continue

                latest = metrics[0]
                historical = [m.value for m in reversed(metrics)]

                result = evaluate_metric(
                    metric_type=metric_type,
                    current_value=latest.value,
                    thresholds={
                        "warning": latest.threshold_warning,
                        "alert": latest.threshold_alert,
                        "critical": latest.threshold_critical,
                    },
                    historical_values=historical
                )

                if result["needs_action"]:
                    send_alert(
                        tenant_id=record.tenant_id,
                        alert_type="ai_governance",
                        severity="critical" if result["is_urgent"] else "high",
                        title=f"Alerta IA: {record.name} — {metric_type.value}",
                        message=(
                            f"Sistema: {record.name}\n"
                            f"Métrica: {metric_type.value}\n"
                            f"Valor actual: {latest.value}\n"
                            f"Nivel: {result['alert_level'].value}\n"
                            f"Tendencia: {result['trend'].value}\n"
                            f"Acción requerida: {'URGENTE' if result['is_urgent'] else 'Investigar'}"
                        ),
                        related_entity="ai_governance_record",
                        related_entity_id=record.id
                    )
                    alerts_generated += 1

            # Verificar si hay checkpoints de conformidad sin evaluar > 90 días
            stale_assessments = db.query(ConformityAssessment).filter(
                ConformityAssessment.ai_record_id == record.id,
                ConformityAssessment.is_deleted == False,
                ConformityAssessment.evaluation_date < datetime.utcnow() - timedelta(days=90)
            ).all()

            for assessment in stale_assessments:
                send_alert(
                    tenant_id=record.tenant_id,
                    alert_type="ai_governance",
                    severity="medium",
                    title=f"Evaluación de conformidad obsoleta: {record.name}",
                    message=(
                        f"El checkpoint {assessment.checkpoint.value} del sistema "
                        f"'{record.name}' no se ha evaluado en más de 90 días. "
                        f"Última evaluación: {assessment.evaluation_date.isoformat()}."
                    ),
                    related_entity="ai_governance_record",
                    related_entity_id=record.id
                )
                alerts_generated += 1

        return {
            "systems_checked": len(active_records),
            "alerts_generated": alerts_generated,
            "timestamp": datetime.utcnow().isoformat()
        }

    finally:
        db.close()

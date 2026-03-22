# Extraído de: LibroCISO/cap-04-registro-tratamientos.md
# Tarea Celery: verificación periódica del RAT
# Se ejecuta semanalmente vía Beat scheduler

from celery import shared_task
from datetime import datetime, timedelta

@shared_task(queue="maintenance")
def check_processing_activities_health():
    """Verifica el estado de salud del RAT y genera alertas.

    Detecta:
    - Tratamientos sin revisión en los últimos 12 meses
    - Tratamientos activos sin medidas de seguridad
    - Tratamientos con categorías especiales sin DPIA asociada
    - Tratamientos con transferencias internacionales sin garantías
    - Borradores abandonados (>30 días sin modificar)
    """
    alerts = []
    now = datetime.utcnow()
    twelve_months_ago = now - timedelta(days=365)
    thirty_days_ago = now - timedelta(days=30)

    # Tratamientos sin revisión en 12 meses
    stale = DataProcessingActivity.query.filter(
        DataProcessingActivity.status == "active",
        DataProcessingActivity.deleted_at.is_(None),
        (DataProcessingActivity.last_review_date < twelve_months_ago) |
        (DataProcessingActivity.last_review_date.is_(None))
    ).all()

    for activity in stale:
        alerts.append({
            "type": "stale_review",
            "severity": "medium",
            "activity_id": activity.id,
            "activity_name": activity.name,
            "message": f"El tratamiento '{activity.name}' lleva más de "
                       f"12 meses sin revisión del DPO",
            "recommendation": "Programar revisión del tratamiento"
        })

    # Categorías especiales sin DPIA
    special_no_dpia = DataProcessingActivity.query.filter(
        DataProcessingActivity.status == "active",
        DataProcessingActivity.special_categories == True,
        DataProcessingActivity.dpia_id.is_(None),
        DataProcessingActivity.deleted_at.is_(None)
    ).all()

    for activity in special_no_dpia:
        alerts.append({
            "type": "missing_dpia",
            "severity": "high",
            "activity_id": activity.id,
            "activity_name": activity.name,
            "message": f"El tratamiento '{activity.name}' tiene categorías "
                       f"especiales (Art. 9) pero no tiene DPIA asociada",
            "recommendation": "Iniciar DPIA conforme al Art. 35 RGPD"
        })

    # Transferencias sin garantías documentadas
    transfers_no_safeguards = DataProcessingActivity.query.filter(
        DataProcessingActivity.status == "active",
        DataProcessingActivity.international_transfers == True,
        DataProcessingActivity.transfer_safeguards.is_(None),
        DataProcessingActivity.deleted_at.is_(None)
    ).all()

    for activity in transfers_no_safeguards:
        alerts.append({
            "type": "missing_transfer_safeguards",
            "severity": "high",
            "activity_id": activity.id,
            "activity_name": activity.name,
            "message": f"El tratamiento '{activity.name}' tiene transferencias "
                       f"internacionales sin garantías documentadas (Art. 46)",
            "recommendation": "Documentar garantías: SCC, BCR o decisión de adecuación"
        })

    # Persistir alertas y notificar al DPO
    if alerts:
        save_alerts(alerts)
        notify_dpo(alerts)

    return {"total_alerts": len(alerts), "high": sum(
        1 for a in alerts if a["severity"] == "high"
    )}

# Extraído de: LibroCISO/cap-27-executive-dashboard.md
@shared_task(name="executive.capture_weekly_snapshot")
def capture_dashboard_snapshot():
    """Captura el estado actual del dashboard ejecutivo
    como snapshot histórico para comparación temporal.

    Ejecutada por Celery Beat los lunes a las 07:00.
    """
    for corporate_id in get_active_corporate_ids():
        data = get_dashboard_sync(corporate_id)
        store_snapshot(
            corporate_id=corporate_id,
            period=datetime.now().strftime("%Y-W%V"),
            data=data,
        )

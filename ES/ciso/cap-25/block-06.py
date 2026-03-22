# Extraído de: LibroCISO/cap-25-vigilancia-normativa.md
from celery import shared_task
from datetime import datetime, timedelta, timezone

@shared_task(name="regulatory_watch.check_sources")
def check_regulatory_sources():
    """Tarea periódica: consulta fuentes activas cuya
    última comprobación excede su frecuencia configurada.

    Ejecutada por Celery Beat cada hora.
    """
    now = datetime.now(timezone.utc)
    frequency_map = {
        "hourly": timedelta(hours=1),
        "daily": timedelta(days=1),
        "weekly": timedelta(weeks=1),
    }

    # Obtener fuentes activas que necesitan revisión
    sources = get_active_sources_due_for_check(now, frequency_map)

    for source in sources:
        try:
            # 1. Consultar la fuente (scraping o API)
            new_publications = fetch_source(source)

            # 2. Filtrar publicaciones ya registradas
            new_items = filter_already_known(source.id, new_publications)

            # 3. Crear RegulatoryUpdate por cada nueva publicación
            for pub in new_items:
                create_regulatory_update(source, pub)

            # 4. Actualizar last_checked_at
            update_last_checked(source.id, now)

        except Exception as e:
            # Registrar fallo sin detener el procesamiento
            # de otras fuentes
            log_source_check_failure(source.id, str(e))

    return {
        "sources_checked": len(sources),
        "timestamp": now.isoformat()
    }

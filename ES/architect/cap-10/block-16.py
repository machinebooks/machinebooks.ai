# Extraído de: LibroTecnico/cap-10-automatizacion-rpa.md
@shared_task(queue="automation")
def sync_onedrive_documents():
    """Tarea Celery de heartbeat: se ejecuta cada 15 minutos.

    Detecta ficheros nuevos/modificados y los indexa en el pipeline
    de documentos de la Plataforma.
    """
    from models.sync_state import OneDriveSyncState

    # Recuperar estado del último sync desde DB
    sync_state = OneDriveSyncState.get_or_create()
    last_sync = sync_state.last_successful_sync or (
        datetime.utcnow() - timedelta(hours=24)  # Primer sync: últimas 24h
    )

    credentials = _get_credentials_from_vault("onedrive_service_account")
    syncer = OneDriveSyncBot(
        tenant_id=credentials["tenant_id"],
        client_id=credentials["client_id"],
        client_secret=credentials["client_secret"]
    )

    changed = syncer.list_changed_files(
        site_id=credentials["sharepoint_site_id"],
        drive_id=credentials["drive_id"],
        since=last_sync
    )

    if not changed:
        logger.info(f"OneDrive sync: sin cambios desde {last_sync}")
        return {"status": "ok", "files_processed": 0}

    # Encolar cada fichero para indexación asíncrona
    for file_info in changed:
        index_document_from_onedrive.delay(file_info)

    # Actualizar timestamp del último sync exitoso
    sync_state.last_successful_sync = datetime.utcnow()
    sync_state.save()

    return {"status": "ok", "files_processed": len(changed)}

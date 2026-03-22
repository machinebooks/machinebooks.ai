# Extraído de: LibroTecnico/cap-10-automatizacion-rpa.md
    try:
        with PortalBot(task_id, credentials, redis_client, user_id) as bot:
            _update_task_status(task_id, "running", "Iniciando login...")

            if not bot.login():
                raise RuntimeError("Login fallido — verificar credenciales")

            _update_task_status(task_id, "running", "Extrayendo datos de proyectos...")
            projects = bot.extract_project_list()

            _update_task_status(task_id, "running", f"Sincronizando {len(projects)} proyectos...")
            _sync_projects_to_db(projects)

            _update_task_status(
                task_id, "completed",
                f"Sincronización completada: {len(projects)} proyectos actualizados"
            )

            # Registrar en AuditLog
            _audit_log(
                user_id=user_id,
                action="AUTOMATION_PORTAL_SYNC_COMPLETED",
                severity="INFO",
                details={"task_id": task_id, "projects_synced": len(projects)}
            )

            return {"status": "ok", "projects_synced": len(projects)}


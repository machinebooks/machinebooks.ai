# Extraído de: LibroCISO/cap-21-celery-async.md
from celery.schedules import crontab

app.conf.beat_schedule = {
    # === MANTENIMIENTO ===
    "backup-mysql-diario": {
        "task": "app.tasks.maintenance.backup_database",
        "schedule": crontab(hour=2, minute=0),  # 2:00 AM
        "options": {"queue": "maintenance"},
    },
    "limpiar-ficheros-temporales": {
        "task": "app.tasks.maintenance.cleanup_temp_files",
        "schedule": crontab(hour=3, minute=0),  # 3:00 AM
        "options": {"queue": "maintenance"},
    },
    "rotar-logs-aplicacion": {
        "task": "app.tasks.maintenance.rotate_logs",
        "schedule": crontab(hour=3, minute=30),  # 3:30 AM
        "options": {"queue": "maintenance"},
    },

    # === HEALTH CHECKS ===
    "health-check-servicios": {
        "task": "app.tasks.maintenance.health_check_all",
        "schedule": 900.0,  # Cada 15 minutos (900 segundos)
        "options": {"queue": "maintenance"},
    },

    # === ALERTAS REGULATORIAS ===
    "alertas-vencimiento-brechas": {
        "task": "app.tasks.notifications.check_breach_deadlines",
        "schedule": crontab(hour=8, minute=0),  # 8:00 AM
        "options": {"queue": "notifications"},
    },
    "alertas-vencimiento-derechos": {
        "task": "app.tasks.notifications.check_rights_deadlines",
        "schedule": crontab(hour=8, minute=5),  # 8:05 AM
        "options": {"queue": "notifications"},
    },
    "alertas-dpia-pendientes": {
        "task": "app.tasks.notifications.check_pending_dpias",
        "schedule": crontab(hour=8, minute=10),  # 8:10 AM
        "options": {"queue": "notifications"},
    },
    "alertas-controles-sin-evidencia": {
        "task": "app.tasks.notifications.check_stale_controls",
        "schedule": crontab(hour=8, minute=15),  # 8:15 AM
        "options": {"queue": "notifications"},
    },
    "alertas-auditorias-programadas": {
        "task": "app.tasks.notifications.check_upcoming_audits",
        "schedule": crontab(hour=8, minute=20),  # 8:20 AM
        "options": {"queue": "notifications"},
    },

    # === SINCRONIZACIÓN ===
    "sync-licencias-modulos": {
        "task": "app.tasks.maintenance.sync_module_licenses",
        "schedule": crontab(minute=0),  # Cada hora en punto
        "options": {"queue": "maintenance"},
    },

    # === MÉTRICAS Y RECÁLCULOS ===
    "recalcular-metricas-cumplimiento": {
        "task": "app.tasks.reports.recalculate_compliance_metrics",
        "schedule": crontab(hour=6, minute=0),  # 6:00 AM
        "options": {"queue": "reports"},
    },
}

# Extraído de: LibroTecnico/cap-08-colas-trabajo.md
# Ejemplo didáctico: configuración del planificador Beat
# Patrón: workers/beat_schedule.py

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {

    # ─── Sincronización CRM ────────────────────────────────────────
    "sync-crm-opportunities": {
        "task": "tasks.sync.crm_opportunities",
        "schedule": 300,  # Cada 5 minutos
        "options": {"queue": "crm"},
    },
    "sync-crm-accounts": {
        "task": "tasks.sync.crm_accounts",
        "schedule": 600,  # Cada 10 minutos
        "options": {"queue": "crm"},
    },

    # ─── Compliance y gobernanza IA ────────────────────────────────
    "check-ai-compliance": {
        "task": "tasks.ai.compliance_check",
        "schedule": crontab(minute=0, hour="*/6"),  # Cada 6 horas
        "options": {"queue": "ai"},
    },
    "detect-pii-in-outputs": {
        "task": "tasks.ai.pii_detection",
        "schedule": crontab(minute=0, hour="*/6"),  # Cada 6 horas
        "options": {"queue": "ai"},
    },
    "evaluate-ai-bias": {
        "task": "tasks.ai.bias_evaluation",
        "schedule": crontab(minute=0, hour=6, day_of_week=1),  # Lunes 06:00
        "options": {"queue": "ai"},
    },
    "verify-config-integrity": {
        "task": "tasks.ai.config_integrity_check",
        "schedule": crontab(minute=0, hour="*/12"),  # Cada 12 horas
        "options": {"queue": "ai"},
    },

    # ─── GDPR y limpieza de datos ──────────────────────────────────
    "gdpr-daily-cleanup": {
        "task": "tasks.sync.gdpr_cleanup",
        "schedule": crontab(minute=0, hour=2),  # Diario a las 02:00
        "options": {"queue": "sync"},
    },
    "gdpr-anonymize-old-logs": {
        "task": "tasks.sync.anonymize_audit_logs",
        "schedule": crontab(minute=0, hour=3),  # Diario a las 03:00
        "options": {"queue": "sync"},
    },

    # ─── Indexación y búsqueda ─────────────────────────────────────
    "reindex-meilisearch": {
        "task": "tasks.sync.meilisearch_reindex",
        "schedule": crontab(minute=0, hour=1),  # Diario a las 01:00
        "options": {"queue": "sync"},
    },
    "reindex-rag-vectors": {
        "task": "tasks.documents.reindex_rag",
        "schedule": crontab(minute=0, hour=4),  # Diario a las 04:00
        "options": {"queue": "documents"},
    },

    # ─── Motor de oportunidades ────────────────────────────────────
    "scan-new-opportunities": {
        "task": "tasks.sync.scan_opportunities",
        "schedule": crontab(minute=0, hour="*/12"),  # Cada 12 horas
        "options": {"queue": "sync"},
    },

    # ─── Alertas proactivas ────────────────────────────────────────
    "proactive-opportunity-alerts": {
        "task": "tasks.alerts.proactive_scan",
        "schedule": crontab(minute=0),  # Cada hora
        "options": {"queue": "priority"},
    },

    # ─── Mantenimiento del sistema ─────────────────────────────────
    "cleanup-expired-tasks": {
        "task": "tasks.sync.cleanup_task_results",
        "schedule": crontab(minute=30, hour=0),  # Diario a las 00:30
        "options": {"queue": "sync"},
    },
    "health-check-services": {
        "task": "tasks.sync.platform_health_check",
        "schedule": 300,  # Cada 5 minutos
        "options": {"queue": "default"},
    },
}

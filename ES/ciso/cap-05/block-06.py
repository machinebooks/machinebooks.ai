# Extraído de: LibroCISO/cap-05-dpia-derechos.md
# Configuración Celery Beat — tareas programadas de privacidad

CELERY_BEAT_SCHEDULE = {
    "check-rights-deadlines": {
        "task": "privacy.check_rights_deadlines",
        "schedule": crontab(hour=8, minute=0, day_of_week="1-5"),
        "options": {"queue": "maintenance"},
    },
    "check-dpia-reviews": {
        "task": "privacy.check_dpia_pending_reviews",
        "schedule": crontab(hour=9, minute=0, day_of_week="1"),  # Lunes
        "options": {"queue": "maintenance"},
    },
}

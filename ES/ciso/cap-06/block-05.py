# Extraído de: LibroCISO/cap-06-brechas-encargados-transferencias.md
# Configuración de Beat scheduler para tareas de privacidad
# Fichero: celery_config.py (fragmento)

CELERY_BEAT_SCHEDULE = {
    # ... otras tareas ...
    "check-breach-deadlines": {
        "task": "privacy.check_breach_deadlines",
        "schedule": 3600.0,  # Cada hora (3600 segundos)
        "options": {"queue": "notifications"}
    },
    "check-processor-reviews": {
        "task": "privacy.check_processor_review_dates",
        "schedule": 86400.0,  # Cada 24 horas
        "options": {"queue": "notifications"}
    },
    "check-tia-expiry": {
        "task": "privacy.check_tia_expiry_dates",
        "schedule": 86400.0,  # Cada 24 horas
        "options": {"queue": "notifications"}
    },
}

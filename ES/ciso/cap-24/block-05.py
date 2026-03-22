# Extraído de: LibroCISO/cap-24-calidad-ia.md
# En celery_config.py / beat_schedule
CELERY_BEAT_SCHEDULE = {
    'calculate-ai-quality-metrics-daily': {
        'task': 'ai.calculate_quality_metrics',
        'schedule': crontab(hour=2, minute=0),
        'args': ('daily',),
        'options': {'queue': 'maintenance'},
    },
    'calculate-ai-quality-metrics-weekly': {
        'task': 'ai.calculate_quality_metrics',
        'schedule': crontab(day_of_week=1, hour=3, minute=0),
        'args': ('weekly',),
        'options': {'queue': 'maintenance'},
    },
}

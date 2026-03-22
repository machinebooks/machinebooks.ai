# Extraído de: LibroPQC/cap-22-celery.md
from celery.schedules import crontab

# Configuración Celery
celery_config = {
    'broker_url': 'redis://pqc_redis:6379/0',
    'result_backend': 'redis://pqc_redis:6379/1',

    # Serialización segura: solo JSON, no pickle
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',

    # Límites globales
    'task_acks_late': True,     # ACK después de ejecutar, no antes
    'worker_prefetch_multiplier': 1,  # No pre-cargar tareas

    # Rutas de colas
    'task_routes': {
        'analyze_repository_task': {'queue': 'repository_analysis'},
        'clone_and_analyze_repository_task': {'queue': 'repository_analysis'},
        'analyze_cloud_security_task': {'queue': 'cloud_audit'},
        'scan_url_certificates_task': {'queue': 'certificate_scanning'},
        'ai_code_analysis_task': {'queue': 'ai_analysis'},
        'scheduled_rescan_task': {'queue': 'repository_analysis'},
    },

    # Tareas programadas con Beat
    'beat_schedule': {
        # Cada hora: comprobar qué clientes necesitan re-escaneo
        'check-pending-rescans': {
            'task': 'check_pending_rescans_task',
            'schedule': crontab(minute=0),  # Cada hora en punto
            'options': {'queue': 'repository_analysis'}
        },

        # Cada día a las 03:00: limpiar jobs antiguos
        'cleanup-old-jobs': {
            'task': 'cleanup_old_jobs_task',
            'schedule': crontab(hour=3, minute=0),
            'options': {'queue': 'repository_analysis'}
        },

        # Cada lunes a las 02:00: informe semanal de cambios
        'weekly-change-report': {
            'task': 'generate_weekly_change_report_task',
            'schedule': crontab(
                hour=2, minute=0, day_of_week='monday'
            ),
            'options': {'queue': 'repository_analysis'}
        },
    }
}

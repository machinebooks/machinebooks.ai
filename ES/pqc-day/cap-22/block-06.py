# Extraído de: LibroPQC/cap-22-celery.md
from datetime import datetime, timedelta

# Frecuencia de re-escaneo según plan de suscripción
RESCAN_INTERVALS = {
    'starter': timedelta(days=30),      # Mensual
    'professional': timedelta(days=7),  # Semanal
    'enterprise': timedelta(days=1),    # Diario
    'ultimate': timedelta(hours=12),    # Cada 12 horas
}

@celery_app.task(
    base=DatabaseTask,
    name='check_pending_rescans_task'
)
def check_pending_rescans_task():
    """Tarea maestra Beat: encola re-escaneos según plan.

    Se ejecuta cada hora. Consulta qué organizaciones
    tienen repositorios o configuraciones cloud cuyo
    último escaneo supera el intervalo de su plan.
    """
    from models import Organization, Repository, AnalysisJob

    now = datetime.utcnow()
    enqueued = 0

    organizations = Organization.query.filter_by(
        is_active=True
    ).all()

    for org in organizations:
        interval = RESCAN_INTERVALS.get(
            org.subscription_plan, timedelta(days=30)
        )

        # Repositorios pendientes de re-escaneo
        repos = Repository.query.filter_by(
            organization_id=org.id,
            auto_scan_enabled=True
        ).all()

        for repo in repos:
            last_scan = AnalysisJob.query.filter_by(
                organization_id=org.id,
                repository_id=repo.id,
                status='completed'
            ).order_by(
                AnalysisJob.completed_at.desc()
            ).first()

            if not last_scan or (now - last_scan.completed_at) > interval:
                # Crear nuevo job y encolar tarea
                job = AnalysisJob(
                    organization_id=org.id,
                    repository_id=repo.id,
                    job_type='scheduled_rescan',
                    status='pending'
                )
                db.session.add(job)
                db.session.commit()

                analyze_repository_task.delay(
                    job_id=job.id,
                    repo_url=repo.url,
                    connector_type=repo.connector_type,
                    access_token=repo.encrypted_token,
                    branch=repo.default_branch
                )
                enqueued += 1

    return {'enqueued_rescans': enqueued, 'checked_at': now.isoformat()}

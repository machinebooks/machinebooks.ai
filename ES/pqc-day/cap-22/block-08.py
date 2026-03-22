# Extraído de: LibroPQC/cap-22-celery.md
@celery_app.task(
    base=DatabaseTask,
    name='cleanup_old_jobs_task'
)
def cleanup_old_jobs_task(retention_days=90):
    """Limpieza de jobs antiguos y directorios temporales huérfanos.

    Se ejecuta cada día a las 03:00 vía Beat.
    """
    from datetime import datetime, timedelta
    import glob

    cutoff = datetime.utcnow() - timedelta(days=retention_days)
    deleted_count = 0

    # 1. Limpiar jobs completados/fallidos más antiguos que retention
    old_jobs = AnalysisJob.query.filter(
        AnalysisJob.status.in_(['completed', 'failed']),
        AnalysisJob.created_at < cutoff
    ).all()

    for job in old_jobs:
        # Borrar hallazgos asociados primero (integridad referencial)
        CryptoFinding.query.filter_by(job_id=job.id).delete()
        db.session.delete(job)
        deleted_count += 1

        # Commit cada 50 para no bloquear la BD
        if deleted_count % 50 == 0:
            db.session.commit()

    db.session.commit()

    # 2. Limpiar directorios temporales huérfanos
    # (tareas que fallaron sin ejecutar el finally)
    temp_dirs_cleaned = 0
    temp_base = tempfile.gettempdir()
    for temp_dir in glob.glob(os.path.join(temp_base, 'pqc_*')):
        dir_age = datetime.utcnow() - datetime.fromtimestamp(
            os.path.getmtime(temp_dir)
        )
        if dir_age > timedelta(hours=24):
            shutil.rmtree(temp_dir, ignore_errors=True)
            temp_dirs_cleaned += 1

    return {
        'jobs_deleted': deleted_count,
        'temp_dirs_cleaned': temp_dirs_cleaned
    }

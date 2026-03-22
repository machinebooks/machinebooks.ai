# Extraído de: LibroPQC/cap-22-celery.md
import os
import shutil
import tempfile
from celery import current_app as celery_app
from tasks.base import DatabaseTask
from analyzers.repository_analyzer import RepositoryAnalyzer
from models import AnalysisJob, CryptoFinding
from extensions import db

@celery_app.task(
    base=DatabaseTask,
    bind=True,
    name='analyze_repository_task',
    max_retries=2,
    soft_time_limit=600,    # 10 minutos: aviso
    time_limit=720          # 12 minutos: kill definitivo
)
def analyze_repository_task(self, job_id, repo_url, connector_type,
                            access_token=None, branch='main'):
    """Ciclo completo de análisis criptográfico de un repositorio.

    Fases: clone → scan → save → score → cleanup
    Cada fase actualiza progress_percentage en la BD
    para que el frontend muestre progreso real.
    """
    temp_dir = None
    try:
        # Fase 1: Inicialización (0-10%)
        job = db.session.get(AnalysisJob, job_id)
        if not job:
            raise ValueError(f"Job {job_id} no encontrado")
        job.status = 'running'
        job.stage = 'initializing'
        job.progress_percentage = 5
        db.session.commit()

        # Fase 2: Clonar repositorio (10-30%)
        job.stage = 'cloning'
        job.progress_percentage = 10
        db.session.commit()

        temp_dir = tempfile.mkdtemp(prefix='pqc_repo_')
        connector = _create_connector(connector_type, access_token)
        connector.clone(repo_url, temp_dir, branch=branch)

        job.progress_percentage = 30
        db.session.commit()

        # Fase 3: Escaneo de patrones criptográficos (30-70%)
        job.stage = 'scanning'
        job.progress_percentage = 35
        db.session.commit()

        analyzer = RepositoryAnalyzer()
        findings = analyzer.scan_directory(temp_dir)

        job.progress_percentage = 70
        db.session.commit()

        # Fase 4: Persistir hallazgos (70-90%)
        job.stage = 'saving_results'
        job.progress_percentage = 75
        db.session.commit()

        saved_count = 0
        for finding_data in findings:
            finding = CryptoFinding(
                job_id=job_id,
                organization_id=job.organization_id,
                file_path=finding_data['file_path'],
                line_number=finding_data['line_number'],
                algorithm=finding_data['algorithm'],
                severity=finding_data['severity'],
                description=finding_data['description'],
                pqc_impact=finding_data['pqc_impact'],
                code_snippet=finding_data.get('snippet', ''),
                source='repository_scan'
            )
            db.session.add(finding)
            saved_count += 1

            # Commit cada 100 hallazgos para no acumular
            # objetos en memoria con repositorios grandes
            if saved_count % 100 == 0:
                db.session.commit()
                # Actualizar progreso proporcional
                progress = 75 + int(15 * saved_count / len(findings))
                job.progress_percentage = min(progress, 89)
                db.session.commit()

        db.session.commit()

        # Fase 5: Calcular score PQC (90-100%)
        job.stage = 'calculating_score'
        job.progress_percentage = 90
        db.session.commit()

        pqc_score = _calculate_pqc_score(findings)

        job.status = 'completed'
        job.stage = 'done'
        job.progress_percentage = 100
        job.total_findings = len(findings)
        job.pqc_score = pqc_score
        job.critical_findings = sum(
            1 for f in findings if f['severity'] == 'critical'
        )
        db.session.commit()

        return {
            'job_id': job_id,
            'total_findings': len(findings),
            'pqc_score': pqc_score
        }

    except Exception as exc:
        # Marcar job como fallido con mensaje de error
        try:
            job = db.session.get(AnalysisJob, job_id)
            if job:
                job.status = 'failed'
                # Truncar y sanitizar: no exponer rutas internas
                # ni stack traces al usuario final
                job.error_message = _sanitize_error(str(exc)[:500])
                db.session.commit()
        except Exception:
            db.session.rollback()
        raise  # Re-lanzar para que Celery gestione reintentos

    finally:
        # SIEMPRE limpiar el directorio temporal
        # Independientemente de éxito o fallo
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

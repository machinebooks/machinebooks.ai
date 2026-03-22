# Extraído de: LibroPQC/cap-07-analisis-codigo.md
from celery import Task
from app.extensions import celery, db
from app.models.analysis import AnalysisJob, AnalysisTarget, CryptoFinding
from app.connectors import GitHubConnector, GitLabConnector, BitbucketConnector
from app.analyzers.repository_analyzer import RepositoryAnalyzer
import tempfile, shutil, os, logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Tarea base que gestiona la sesión de BD"""
    def __call__(self, *args, **kwargs):
        try:
            return super().__call__(*args, **kwargs)
        finally:
            db.session.remove()


@celery.task(base=DatabaseTask, bind=True)
def analyze_repository_task(self, job_id: int, target_id: int, config: dict):
    """
    Tarea asíncrona: clonar repositorio, escanear y guardar hallazgos.

    Args:
        job_id:    ID del AnalysisJob
        target_id: ID del AnalysisTarget
        config:    {'type': 'github|gitlab|bitbucket',
                    'credentials': {...},
                    'repo': 'owner/name'}
    """
    target = AnalysisTarget.query.get(target_id)
    job = AnalysisJob.query.get(job_id)

    target.status = 'analyzing'
    target.started_at = datetime.utcnow()
    db.session.commit()

    temp_dir = tempfile.mkdtemp(prefix='pqc_analysis_')

    try:
        # 1. Clonar según tipo de conector
        connector_type = config.get('type', 'github')
        credentials = config.get('credentials', {})

        if connector_type == 'github':
            connector = GitHubConnector(credentials)
            connector.clone_repository(config['repo'], temp_dir)
        elif connector_type == 'gitlab':
            connector = GitLabConnector(credentials)
            connector.clone_project(config['project_id'], temp_dir)
        elif connector_type == 'bitbucket':
            connector = BitbucketConnector(credentials)
            connector.clone_repository(
                config['workspace'], config['repo_slug'], temp_dir
            )

        target.progress_percentage = 30
        db.session.commit()

        # 2. Escanear con el RepositoryAnalyzer
        analyzer = RepositoryAnalyzer(base_path=temp_dir)
        findings = analyzer.scan_directory(temp_dir)

        target.progress_percentage = 70
        db.session.commit()

        # 3. Guardar cada hallazgo en la tabla CryptoFinding
        for f in findings:
            crypto_finding = CryptoFinding(
                job_id=job_id,
                target_id=target_id,
                finding_type='algorithm',
                algorithm_name=f.algorithm,
                algorithm_category=_classify_algorithm(f.algorithm),
                risk_level=f.severity,
                pqc_compliant=f.algorithm in PQC_SAFE_ALGORITHMS,
                location=f.file_path,
                context=f.code_snippet,
                description=f.description,
                recommendation=f.recommendation,
            )
            db.session.add(crypto_finding)

        # 4. Calcular score PQC
        summary = analyzer.get_summary()
        pqc_score = summary['pqc_readiness_score']

        # 5. Cerrar target y actualizar job
        target.status = 'completed'
        target.progress_percentage = 100
        target.completed_at = datetime.utcnow()

        job.targets_completed += 1
        job.findings_count += len(findings)
        job.critical_findings += summary['critical_count']
        job.high_findings += summary['high_count']

        if job.targets_completed >= job.targets_total:
            job.status = 'completed'
            job.completed_at = datetime.utcnow()

        db.session.commit()

        return {'status': 'success', 'findings_count': len(findings),
                'pqc_score': pqc_score}

    except Exception as e:
        logger.error(f"Error en análisis de repositorio: {e}", exc_info=True)
        target.status = 'failed'
        # Registrar el error completo en logs internos,
        # pero no exponer str(e) en respuestas externas.
        target.error_message = str(e)[:500]
        job.status = 'failed'
        db.session.commit()
        return {'status': 'error', 'message': 'Error en análisis de repositorio'}

    finally:
        # Siempre limpiar el directorio temporal
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

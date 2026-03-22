# Extraído de: LibroPQC/cap-22-celery.md
from flask import request, jsonify
from flask_restful import Resource
from auth.decorators import require_auth, require_role
from models import AnalysisJob, Repository
from tasks.analysis_tasks import analyze_repository_task
from extensions import db


class RepositoryAnalysisResource(Resource):
    @require_auth
    @require_role('analyst', 'admin', 'org_owner')
    def post(self, repository_id):
        """Lanzar análisis criptográfico de un repositorio.

        Retorna inmediatamente con el job_id.
        El frontend consulta GET /jobs/{job_id} para progreso.
        """
        user = request.current_user
        repo = Repository.query.filter_by(
            id=repository_id,
            organization_id=user.organization_id
        ).first_or_404()

        # Verificar que no hay un análisis en curso
        active_job = AnalysisJob.query.filter_by(
            repository_id=repo.id,
            status='running'
        ).first()
        if active_job:
            return {
                'error': 'Ya hay un análisis en curso',
                'job_id': active_job.id
            }, 409  # Conflict

        # Crear job y encolar tarea
        job = AnalysisJob(
            organization_id=user.organization_id,
            repository_id=repo.id,
            job_type='manual_scan',
            status='pending',
            launched_by=user.id
        )
        db.session.add(job)
        db.session.commit()

        # .delay() encola la tarea en Redis y retorna inmediatamente
        analyze_repository_task.delay(
            job_id=job.id,
            repo_url=repo.url,
            connector_type=repo.connector_type,
            access_token=repo.get_decrypted_token(),
            branch=repo.default_branch or 'main'
        )

        return {
            'job_id': job.id,
            'status': 'pending',
            'message': 'Análisis encolado'
        }, 202  # Accepted


class AnalysisJobStatusResource(Resource):
    @require_auth
    def get(self, job_id):
        """Consultar progreso de un análisis.

        El frontend llama cada 3-5 segundos hasta
        que status sea 'completed' o 'failed'.
        """
        user = request.current_user
        job = AnalysisJob.query.filter_by(
            id=job_id,
            organization_id=user.organization_id
        ).first_or_404()

        response = {
            'job_id': job.id,
            'status': job.status,
            'stage': job.stage,
            'progress_percentage': job.progress_percentage,
            'progress_message': job.progress_message,
        }

        if job.status == 'completed':
            response.update({
                'total_findings': job.total_findings,
                'pqc_score': job.pqc_score,
                'critical_findings': job.critical_findings,
            })
        elif job.status == 'failed':
            response['error_message'] = job.error_message

        return response, 200

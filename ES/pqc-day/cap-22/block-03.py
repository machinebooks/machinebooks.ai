# Extraído de: LibroPQC/cap-22-celery.md
from celery.exceptions import MaxRetriesExceededError

@celery_app.task(
    base=DatabaseTask,
    bind=True,
    name='analyze_cloud_security_task',
    max_retries=3,
    default_retry_delay=60,
    rate_limit='2/m',       # Máximo 2 ejecuciones por minuto
    queue='cloud_audit'
)
def analyze_cloud_security_task(self, job_id, cloud_config_id):
    """Auditoría criptográfica de configuración cloud.

    Incluye retry automático con backoff para rate limits
    de las APIs de AWS, Azure y GCP.
    """
    try:
        job = db.session.get(AnalysisJob, job_id)
        config = db.session.get(CloudConfiguration, cloud_config_id)

        if not job or not config:
            raise ValueError("Job o configuración cloud no encontrados")

        _update_progress(job, 'initializing', 5,
                         f'Conectando a {config.provider}')

        # Crear escáner según proveedor
        scanner = _create_cloud_scanner(config)

        _update_progress(job, 'connecting', 10,
                         'Verificando credenciales')

        if not scanner.test_connection():
            raise ConnectionError(
                f"Credenciales inválidas para {config.provider}"
            )

        _update_progress(job, 'scanning', 15,
                         f'Escaneando servicios {config.provider}')

        # Escaneo por servicios con progreso granular
        findings = []
        services = scanner.get_scannable_services()
        for i, service in enumerate(services):
            try:
                service_findings = scanner.scan_service(service)
                findings.extend(service_findings)
            except ThrottlingError as e:
                # Rate limit del proveedor: esperar y reintentar
                # la tarea completa con backoff exponencial
                retry_delay = 60 * (2 ** self.request.retries)
                raise self.retry(
                    exc=e,
                    countdown=retry_delay,
                    max_retries=3
                )

            progress = 15 + int(65 * (i + 1) / len(services))
            _update_progress(
                job, 'scanning', progress,
                f'Servicio {service}: {len(service_findings)} hallazgos'
            )

        # Clasificación cuántica de hallazgos
        _update_progress(job, 'classifying', 82,
                         'Clasificando vulnerabilidad cuántica')

        classified = _classify_quantum_vulnerability(findings)

        # Persistir hallazgos
        _update_progress(job, 'saving_results', 88,
                         f'Guardando {len(classified)} hallazgos')

        _save_cloud_findings(job, classified)

        # Cierre
        pqc_score = _calculate_cloud_pqc_score(classified)
        job.status = 'completed'
        job.progress_percentage = 100
        job.total_findings = len(classified)
        job.pqc_score = pqc_score
        db.session.commit()

        return {
            'job_id': job_id,
            'provider': config.provider,
            'total_findings': len(classified)
        }

    except MaxRetriesExceededError:
        _mark_job_failed(
            job_id,
            Exception(
                f"Agotados {self.max_retries} reintentos. "
                f"La API de {config.provider} no responde. "
                f"Reintente más tarde."
            )
        )
        raise

    except Exception as exc:
        _mark_job_failed(job_id, exc)
        raise

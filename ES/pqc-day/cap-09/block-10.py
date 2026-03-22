# Extraído de: LibroPQC/cap-09-auditoria-cloud.md
# Ejemplo didáctico: tasks/cloud_scan_tasks.py

@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def scan_cloud_config_task(self, job_id: int, config_id: int,
                           regions: list = None, options: dict = None):
    """Ejecuta escaneo cloud en segundo plano"""

    job = AnalysisJob.query.get(job_id)
    config = ClientCloudConfig.query.get(config_id)
    if not job or not config:
        return {'status': 'error', 'message': 'Not found'}

    provider = config.provider
    regions = regions or ['us-east-1', 'us-west-2', 'eu-west-1']

    try:
        # Actualizar progreso: inicializando
        job.status = 'running'
        job.progress_percentage = 5
        job_config = job.configuration or {}
        job_config['stage'] = 'initializing'
        job.configuration = job_config
        db.session.commit()

        # Crear escáner según proveedor
        if provider.name == 'aws':
            scanner = AWSCloudScanner(config.credentials, regions)
            job_config['stage'] = 'connecting'
            job.progress_percentage = 10
            db.session.commit()

            job_config['stage'] = 'scanning_aws'
            job.progress_percentage = 15
            db.session.commit()

            result = scanner.scan_all(
                progress_callback=lambda svc: _update_progress(
                    job, job_config, scanner, svc
                )
            )
        elif provider.name == 'azure':
            scanner = AzureCloudScanner(config.credentials)
            result = scanner.scan_all()
        elif provider.name == 'gcp':
            scanner = GCPCloudScanner(config.credentials)
            result = scanner.scan_all()

        # Guardar hallazgos en base de datos
        job_config['stage'] = 'saving_results'
        job.progress_percentage = 90
        db.session.commit()

        for finding in result.findings:
            crypto_finding = CryptoFinding(
                job_id=job_id,
                finding_type='configuration',
                algorithm_category='cloud_security',
                risk_level=finding.severity,
                pqc_compliant=(finding.pqc_impact == 'none'),
                location=f"{finding.region}:{finding.resource_id}",
                description=f"{finding.title}: {finding.description}",
                recommendation=finding.pqc_recommendation,
            )
            db.session.add(crypto_finding)

        # Completar trabajo
        job.status = 'completed'
        job.progress_percentage = 100
        job.result_summary = {
            'provider': result.provider,
            'regions_scanned': result.regions_scanned,
            'total_resources': result.total_resources,
            'findings_count': result.findings_count,
            'pqc_readiness_score': round(result.pqc_readiness_score, 2)
        }
        db.session.commit()

        return {'status': 'completed', 'job_id': job_id,
                'pqc_readiness_score': round(result.pqc_readiness_score, 2)}

    except Exception as e:
        job.status = 'failed'
        # Registrar internamente; truncar para evitar almacenar
        # trazas completas con datos sensibles en la BD.
        job.error_message = str(e)[:500]
        db.session.commit()

        # Reintentar en errores de rate limiting
        error_msg = str(e).lower()
        if 'rate limit' in error_msg or 'throttl' in error_msg:
            raise self.retry(exc=e)

        return {'status': 'failed', 'job_id': job_id,
                'error': 'Error en escaneo cloud'}

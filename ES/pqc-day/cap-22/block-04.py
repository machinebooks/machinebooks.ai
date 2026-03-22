# Extraído de: LibroPQC/cap-22-celery.md
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

@celery_app.task(
    base=DatabaseTask,
    bind=True,
    name='scan_url_certificates_task',
    max_retries=1,
    soft_time_limit=300,
    queue='certificate_scanning'
)
def scan_url_certificates_task(self, job_id, urls, scan_config_id=None):
    """Escaneo de certificados SSL/TLS para una lista de URLs.

    Usa ThreadPoolExecutor para paralelizar handshakes TLS.
    Timeout de 15 segundos por URL para evitar bloqueos
    por servidores que no responden.
    """
    try:
        job = db.session.get(AnalysisJob, job_id)
        if not job:
            raise ValueError(f"Job {job_id} no encontrado")

        _update_progress(job, 'initializing', 5,
                         f'Preparando escaneo de {len(urls)} URLs')

        scanner = URLCertificateScanner(
            timeout=15, allow_insecure_fallback=True
        )
        results = []
        errors = []

        # Paralelizar handshakes con ThreadPoolExecutor
        # max_workers=5 es conservador: evita saturar
        # la conexión de red y disparar alertas IDS
        max_workers = min(5, len(urls))
        _update_progress(job, 'scanning', 10,
                         f'Escaneando con {max_workers} hilos')

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Mapear futures a URLs para tracking
            future_to_url = {
                executor.submit(scanner.scan_url, url): url
                for url in urls
            }

            completed = 0
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                completed += 1

                try:
                    # Timeout individual por URL: 15 segundos
                    cert_info = future.result(timeout=15)
                    results.append({
                        'url': url,
                        'certificate': cert_info,
                        'status': 'success'
                    })
                except TimeoutError:
                    errors.append({
                        'url': url,
                        'error': 'Timeout tras 15 segundos',
                        'status': 'timeout'
                    })
                except Exception as e:
                    errors.append({
                        'url': url,
                        'error': str(e)[:200],
                        'status': 'error'
                    })

                # Progreso proporcional
                progress = 10 + int(70 * completed / len(urls))
                _update_progress(
                    job, 'scanning', progress,
                    f'{completed}/{len(urls)} URLs procesadas'
                )

        # Clasificación cuántica de certificados
        _update_progress(job, 'classifying', 82,
                         'Evaluando vulnerabilidad post-cuántica')

        findings = []
        for result in results:
            cert = result['certificate']
            finding = _classify_certificate_pqc(
                url=result['url'],
                key_algorithm=cert.get('key_algorithm'),
                key_size=cert.get('key_size'),
                signature_algorithm=cert.get('signature_algorithm'),
                tls_version=cert.get('tls_version'),
                expiry_date=cert.get('not_after')
            )
            findings.append(finding)

        # Persistir
        _update_progress(job, 'saving_results', 88,
                         f'Guardando {len(findings)} hallazgos')
        _save_certificate_findings(job, findings, errors)

        job.status = 'completed'
        job.progress_percentage = 100
        job.total_findings = len(findings)
        job.progress_message = (
            f'{len(results)} certificados analizados, '
            f'{len(errors)} errores'
        )
        db.session.commit()

        return {
            'job_id': job_id,
            'scanned': len(results),
            'errors': len(errors),
            'findings': len(findings)
        }

    except Exception as exc:
        _mark_job_failed(job_id, exc)
        raise

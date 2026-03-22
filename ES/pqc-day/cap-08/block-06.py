# Extraído de: LibroPQC/cap-08-certificados.md
@celery.task(base=DatabaseTask, bind=True)
def scan_url_certificates_task(self, job_id: int, urls: list,
                                target_id: int = None):
    """Escanear URLs para analizar certificados y configuración TLS"""
    job = AnalysisJob.query.get(job_id)
    if not job:
        return {'status': 'error', 'message': 'Job not found'}

    # Crear target si no existe
    if target_id is None:
        target = AnalysisTarget(
            job_id=job_id,
            target_type='domain',
            target_identifier=', '.join(urls[:5]),
            target_metadata={'urls': urls, 'count': len(urls)},
            analysis_status='scanning'
        )
        db.session.add(target)
        db.session.commit()
        target_id = target.id

    job.status = 'running'
    job.progress_percentage = 10
    db.session.commit()

    # Crear scanner con timeout de 15s y fallback inseguro
    # habilitado para modo auditoría (inspeccionar certificados inválidos)
    scanner = URLCertificateScanner(
        timeout=15, allow_insecure_fallback=True
    )

    # Leer configuración de profundidad del job
    depth = job.configuration.get('depth', 'standard')
    analysis_type = job.configuration.get('analysis_type', 'web_application')
    discover_subdomains = depth in ['standard', 'deep', 'comprehensive']

    # Escanear con paralelismo de 5 hilos
    results = scanner.scan_urls(
        urls, max_workers=5, depth=depth,
        discover_subdomains=discover_subdomains,
        analysis_type=analysis_type
    )

    # Persistir cada resultado como CryptoFinding
    for result in results:
        if result.is_valid:
            risk_level = 'critical' if result.pqc_readiness_score < 30 \
                    else 'high'     if result.pqc_readiness_score < 50 \
                    else 'medium'   if result.pqc_readiness_score < 70 \
                    else 'low'

            crypto_finding = CryptoFinding(
                job_id=job_id,
                target_id=target_id,
                finding_type='certificate',
                algorithm_name=f"{result.public_key_type}-{result.public_key_bits}",
                algorithm_category='asymmetric',
                risk_level=risk_level,
                pqc_compliant=result.pqc_readiness_score >= 80,
                location=result.url,
                context=f"TLS {result.tls_version}, "
                        f"Cipher: {result.cipher_suite}",
                description=f"Certificate using {result.signature_algorithm}",
                recommendation='Migrate to PQC algorithms (ML-KEM, ML-DSA)',
                cve_reference_links={
                    'tls_version': result.tls_version,
                    'cipher_suite': result.cipher_suite,
                    'signature_algorithm': result.signature_algorithm,
                    'pqc_readiness_score': result.pqc_readiness_score,
                    'findings': [f.to_dict() if hasattr(f, 'to_dict')
                                 else f for f in result.findings]
                }
            )
            db.session.add(crypto_finding)
    db.session.commit()

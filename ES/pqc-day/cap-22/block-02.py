# Extraído de: LibroPQC/cap-22-celery.md
@celery_app.task(
    base=DatabaseTask,
    bind=True,
    name='clone_and_analyze_repository_task',
    max_retries=1,
    soft_time_limit=1800,   # 30 minutos: repos grandes + IA
    time_limit=2100         # 35 minutos: kill
)
def clone_and_analyze_repository_task(self, job_id, repo_url,
                                      connector_type, access_token=None,
                                      branch='main', include_owasp=True,
                                      include_ai=False):
    """Análisis completo de repositorio en 6 etapas.

    Etapas:
    1. Inicialización y validación       (0-5%)
    2. Clonación del repositorio         (5-20%)
    3. Escaneo de patrones criptográficos (20-45%)
    4. Análisis OWASP (Bandit + Semgrep)  (45-65%)
    5. Análisis semántico con IA          (65-85%)
    6. Cálculo de scores y cierre         (85-100%)
    """
    temp_dir = None
    try:
        job = db.session.get(AnalysisJob, job_id)
        if not job:
            raise ValueError(f"Job {job_id} no encontrado")

        # ---- Etapa 1: Inicialización ----
        _update_progress(job, 'initializing', 2,
                         'Validando parámetros de conexión')

        connector = _create_connector(connector_type, access_token)
        if not connector.test_connection(repo_url):
            raise ConnectionError(
                f"No se pudo conectar al repositorio: {repo_url}"
            )

        _update_progress(job, 'initializing', 5,
                         'Conexión verificada')

        # ---- Etapa 2: Clonación ----
        _update_progress(job, 'cloning', 8,
                         'Clonando repositorio...')

        temp_dir = tempfile.mkdtemp(prefix='pqc_full_')
        connector.clone(repo_url, temp_dir, branch=branch)

        file_count = _count_source_files(temp_dir)
        _update_progress(job, 'cloning', 20,
                         f'Repositorio clonado: {file_count} ficheros fuente')

        # ---- Etapa 3: Escaneo criptográfico ----
        _update_progress(job, 'crypto_scan', 22,
                         'Iniciando escaneo de patrones criptográficos')

        analyzer = RepositoryAnalyzer()
        crypto_findings = analyzer.scan_directory(temp_dir)
        _save_findings_batch(job, crypto_findings, 'repository_scan')

        _update_progress(job, 'crypto_scan', 45,
                         f'{len(crypto_findings)} hallazgos criptográficos')

        # ---- Etapa 4: OWASP (opcional) ----
        owasp_findings = []
        if include_owasp:
            _update_progress(job, 'owasp_scan', 48,
                             'Ejecutando Bandit + Semgrep')

            from analyzers.owasp_analyzer import OWASPAnalyzer
            owasp = OWASPAnalyzer()
            owasp_findings = owasp.scan_directory(temp_dir)
            _save_findings_batch(job, owasp_findings, 'owasp_scan')

            _update_progress(job, 'owasp_scan', 65,
                             f'{len(owasp_findings)} hallazgos OWASP')
        else:
            _update_progress(job, 'owasp_scan', 65,
                             'Análisis OWASP omitido')

        # ---- Etapa 5: IA (opcional) ----
        ai_findings = []
        if include_ai:
            _update_progress(job, 'ai_analysis', 68,
                             'Enviando ficheros relevantes a Claude')

            from analyzers.ai_code_analyzer import AICodeAnalyzer
            ai_analyzer = AICodeAnalyzer()
            # Solo analizar ficheros con hallazgos criptográficos
            relevant_files = set(f['file_path'] for f in crypto_findings)
            ai_findings = ai_analyzer.analyze_files(
                temp_dir, list(relevant_files)
            )
            _save_findings_batch(job, ai_findings, 'ai_analysis')

            _update_progress(job, 'ai_analysis', 85,
                             f'{len(ai_findings)} hallazgos de IA')
        else:
            _update_progress(job, 'ai_analysis', 85,
                             'Análisis IA omitido')

        # ---- Etapa 6: Cierre ----
        all_findings = crypto_findings + owasp_findings + ai_findings
        pqc_score = _calculate_pqc_score(all_findings)

        job.status = 'completed'
        job.stage = 'done'
        job.progress_percentage = 100
        job.total_findings = len(all_findings)
        job.pqc_score = pqc_score
        job.progress_message = (
            f'Completado: {len(all_findings)} hallazgos, '
            f'score PQC: {pqc_score}%'
        )
        db.session.commit()

        return {
            'job_id': job_id,
            'crypto_findings': len(crypto_findings),
            'owasp_findings': len(owasp_findings),
            'ai_findings': len(ai_findings),
            'pqc_score': pqc_score
        }

    except Exception as exc:
        _mark_job_failed(job_id, exc)
        raise

    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


def _update_progress(job, stage, percentage, message=''):
    """Función auxiliar para actualizar progreso del job."""
    job.stage = stage
    job.progress_percentage = percentage
    job.progress_message = message
    db.session.commit()

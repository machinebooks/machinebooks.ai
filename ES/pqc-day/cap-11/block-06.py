# Extraído de: LibroPQC/cap-11-analisis-semantico.md
# Ejemplo didáctico: tasks/ai_analysis_tasks.py — stages del pipeline

# STAGE 1-4: Parsear URL, obtener info, clonar repo, recolectar ficheros
# (hasta 10.000 ficheros de código, excluir node_modules/.git/etc.)

# STAGE 5: Análisis de patrones (regex) — rápido, sin IA
pattern_analyzer = RepositoryAnalyzer()
for file_info in code_files:
    pattern_findings.extend(
        pattern_analyzer.analyze_file_content(
            file_info['content'], file_info['path']
        )
    )

# STAGE 5.5: Análisis OWASP por patrones (si está activado)

# STAGE 6A: Análisis IA para PQC — en lotes de 10
if analyze_pqc and ai_available:
    analyzer = AICodeAnalyzer(
        provider=ai_provider,
        analysis_type='pqc',
        **ai_config
    )
    max_ai_files = options.get('max_ai_files', 100)
    batch_size = options.get('ai_batch_size', 10)

    for batch_start in range(0, len(files_for_ai), batch_size):
        batch = files_for_ai[batch_start:batch_start + batch_size]
        for file_info in batch:
            result = analyzer.analyze_file(
                code=file_info['content'],
                filename=file_info['path'],
                context={'focus': 'pqc'}
            )
            # Extraer findings, filtrar OWASP, añadir a ai_pqc_findings

# STAGE 6B: Análisis IA para OWASP (si está activado)

# STAGE 7: Combinar y deduplicar hallazgos PQC (pattern + AI)
# STAGE 8: Persistir en BD (CryptoFinding + VulnerabilityFinding)
# STAGE 9: Calcular risk_score y finalizar

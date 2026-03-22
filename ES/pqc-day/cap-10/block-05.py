# Extraído de: LibroPQC/cap-10-owasp.md
# Ejemplo didáctico: tasks/ai_analysis_tasks.py — persistencia OWASP

# STAGE 5.5: Análisis de vulnerabilidades OWASP
analyze_owasp = options.get('analyze_owasp', False)

if analyze_owasp:
    update_stage('owasp_pattern_analysis',
                 files_count=len(code_files),
                 message='Analizando vulnerabilidades OWASP Top 10...')

    from app.analyzers.owasp_analyzer import OWASPAnalyzer
    owasp_analyzer = OWASPAnalyzer()

    # Análisis completo del repositorio
    owasp_result = owasp_analyzer.analyze_files(code_files)
    owasp_findings = owasp_result.get('findings', [])
    owasp_summary = owasp_analyzer.get_owasp_summary(owasp_findings)

    # Persistir cada hallazgo como VulnerabilityFinding
    for owasp_finding in owasp_findings:
        vuln_finding = VulnerabilityFinding(
            job_id=job.id,
            target_id=target.id,
            vulnerability_type='owasp',
            severity=owasp_finding.get('severity', 'medium'),
            cwe_id=owasp_finding.get('cwe'),
            description=owasp_finding.get('description', ''),
            affected_component=owasp_finding.get('file_path', ''),
            remediation=owasp_finding.get('recommendation', ''),
            reference_links={
                'owasp_id': owasp_finding.get('owasp_id'),
                'rule_id': owasp_finding.get('rule_id'),
                'code_snippet': owasp_finding.get('code_snippet', '')[:500]
            },
            quantum_threat=False  # Por defecto, sin amenaza cuántica
        )
        db.session.add(vuln_finding)

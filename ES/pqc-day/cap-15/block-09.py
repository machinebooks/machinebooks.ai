# Extraído de: LibroPQC/cap-15-nis2.md
def ai_suggest_control_mappings(self, assessment_id):
    """Usar IA para sugerir mapeos de hallazgos a controles"""
    assessment = ComplianceAssessment.query.get(assessment_id)

    # Obtener controles aún no evaluados
    unmapped_cas = ControlAssessment.query.filter(
        ControlAssessment.assessment_id == assessment_id,
        ControlAssessment.implementation_status == 'not_assessed'
    ).all()

    # Recopilar todos los hallazgos de los análisis importados
    all_findings = []
    code_ids = json.loads(assessment.imported_code_analysis_ids or '[]')
    for aid in code_ids:
        analysis = AnalysisJob.query.get(aid)
        if analysis:
            for f in analysis.crypto_findings:
                all_findings.append({
                    'id': f.id, 'type': 'crypto',
                    'algorithm': f.algorithm,
                    'severity': f.severity,
                    'description': f.description
                })

    # Construir prompt con contexto regulatorio
    controls_text = "\n".join([
        f"- {ca.control.reference}: {ca.control.title}"
        for ca in unmapped_cas[:50]
    ])
    findings_text = "\n".join([
        f"- Finding {f['id']}: {f.get('algorithm', 'N/A')} ({f['severity']})"
        for f in all_findings[:30]
    ])

    prompt = f"""Eres un auditor de compliance especializado en NIS2 y
    criptografía post-cuántica.

    Hallazgos de seguridad detectados:
    {findings_text}

    Controles pendientes de evaluar:
    {controls_text}

    Para cada hallazgo, indica qué controles se ven afectados:
    - "violation": El control NO se cumple
    - "partial": El control se cumple parcialmente
    - "ok": El hallazgo no afecta al control

    Responde en JSON con razonamiento explícito:
    [{{"finding_id": 1, "control_ref": "NIS2.RISK.8",
       "impact": "violation", "reasoning": "..."}}]
    """

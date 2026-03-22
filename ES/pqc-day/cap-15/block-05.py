# Extraído de: LibroPQC/cap-15-nis2.md
def import_findings_to_assessment(self, assessment_id,
                                   code_analysis_ids=None,
                                   cloud_analysis_ids=None):
    """Importar hallazgos técnicos y mapearlos a controles NIS2/DORA/ISO"""
    assessment = ComplianceAssessment.query.get(assessment_id)
    framework = assessment.framework
    results = {
        'code_findings_processed': 0,
        'cloud_findings_processed': 0,
        'controls_updated': 0,
        'mappings_created': 0
    }

    # Cargar todos los controles del framework en un dict por referencia
    controls = {
        c.reference: c
        for c in ComplianceControl.query.filter_by(
            framework_id=framework.id
        ).all()
    }

    # Procesar análisis de código
    if code_analysis_ids:
        for analysis_id in code_analysis_ids:
            analysis = AnalysisJob.query.get(analysis_id)
            if not analysis:
                continue
            # Procesar hallazgos criptográficos
            for finding in analysis.crypto_findings:
                results['code_findings_processed'] += 1
                mappings = self._map_finding_to_controls(
                    finding, 'crypto', controls, framework.code
                )
                for control_ref, mapping_data in mappings.items():
                    self._update_control_assessment(
                        assessment_id, controls.get(control_ref),
                        finding, 'code_analysis', mapping_data
                    )
                    results['mappings_created'] += 1

            # Procesar hallazgos de vulnerabilidades
            for finding in analysis.vulnerability_findings:
                results['code_findings_processed'] += 1
                mappings = self._map_finding_to_controls(
                    finding, 'vulnerability', controls, framework.code
                )
                for control_ref, mapping_data in mappings.items():
                    self._update_control_assessment(
                        assessment_id, controls.get(control_ref),
                        finding, 'code_analysis', mapping_data
                    )
                    results['mappings_created'] += 1

    db.session.commit()
    return results

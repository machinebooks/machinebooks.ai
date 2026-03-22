# Extraído de: LibroPQC/cap-15-nis2.md
def generate_soa(self, assessment_id, format_type='json'):
    """Generar Statement of Applicability para auditoría"""
    assessment = ComplianceAssessment.query.get(assessment_id)

    # Obtener evaluaciones con sus controles, ordenadas
    control_assessments = db.session.query(
        ControlAssessment, ComplianceControl
    ).join(
        ComplianceControl,
        ControlAssessment.control_id == ComplianceControl.id
    ).filter(
        ControlAssessment.assessment_id == assessment_id
    ).order_by(ComplianceControl.sequence_order).all()

    soa_data = {
        'assessment': {
            'name': assessment.name,
            'client': assessment.client.name,
            'framework': assessment.framework.name,
            'date': assessment.assessment_date.isoformat(),
            'overall_score': assessment.overall_score
        },
        'summary': {
            'total': len(control_assessments),
            'implemented': assessment.implemented_controls,
            'partial': assessment.partial_controls,
            'not_implemented': assessment.not_implemented_controls,
            'not_applicable': assessment.not_applicable_controls
        },
        'controls': [{
            'reference': control.reference,
            'title': control.title,
            'domain': control.domain,
            'is_applicable': ca.is_applicable,
            'implementation_status': ca.implementation_status,
            'effectiveness': ca.effectiveness_level,
            'evidence': ca.evidence_description,
            'findings': ca.findings,
            'recommendations': ca.recommendations
        } for ca, control in control_assessments]
    }
    return soa_data

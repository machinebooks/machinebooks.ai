# Extraído de: LibroPQC/cap-15-nis2.md
def generate_compliance_report(self, assessment_id, format_type='json'):
    """Generar informe completo con estadísticas por dominio"""
    assessment = ComplianceAssessment.query.get(assessment_id)
    soa = self.generate_soa(assessment_id, 'json')

    # Estadísticas agrupadas por dominio normativo
    domain_stats = db.session.query(
        ComplianceControl.domain,
        db.func.count(ControlAssessment.id).label('total'),
        db.func.sum(db.case(
            (ControlAssessment.implementation_status == 'implemented', 1),
            else_=0)).label('implemented'),
        db.func.sum(db.case(
            (ControlAssessment.implementation_status == 'partial', 1),
            else_=0)).label('partial'),
        db.func.sum(db.case(
            (ControlAssessment.implementation_status == 'not_implemented', 1),
            else_=0)).label('not_implemented')
    ).join(
        ControlAssessment,
        ControlAssessment.control_id == ComplianceControl.id
    ).filter(
        ControlAssessment.assessment_id == assessment_id
    ).group_by(ComplianceControl.domain).all()

    report = {
        'title': f'Informe de Cumplimiento NIS2 - {assessment.name}',
        'executive_summary': {
            'overall_compliance': assessment.overall_score,
            'gaps_identified': (assessment.not_implemented_controls
                                + assessment.partial_controls),
        },
        'compliance_by_domain': [{
            'domain': d.domain,
            'total': d.total,
            'implemented': d.implemented or 0,
            'partial': d.partial or 0,
            'not_implemented': d.not_implemented or 0,
            'compliance_rate': round(
                ((d.implemented or 0) * 100 + (d.partial or 0) * 50)
                / d.total, 1
            ) if d.total > 0 else 0
        } for d in domain_stats],
        'soa': soa,
        'recommendations': self._generate_recommendations(assessment_id)
    }
    return report

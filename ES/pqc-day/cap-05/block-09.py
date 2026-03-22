# Extraído de: LibroPQC/cap-05-modelo-datos.md
# Query: hallazgos críticos no-PQC por framework de compliance
def get_critical_non_pqc_by_framework(client_id):
    """
    Obtiene hallazgos criptográficos críticos no PQC-compliant
    agrupados por framework normativo vinculado.
    """
    results = db.session.query(
        ComplianceFramework.code,
        ComplianceFramework.name,
        ComplianceControl.reference,
        ComplianceControl.title,
        CryptoFinding.algorithm_name,
        CryptoFinding.risk_level,
        CryptoFinding.location,
        CryptoFinding.context,
        FindingControlMapping.confidence
    ).join(
        ComplianceControl,
        ComplianceControl.framework_id == ComplianceFramework.id
    ).join(
        FindingControlMapping,
        FindingControlMapping.control_id == ComplianceControl.id
    ).join(
        CryptoFinding,
        db.and_(
            FindingControlMapping.finding_type == 'crypto',
            FindingControlMapping.finding_id == CryptoFinding.id
        )
    ).join(
        AnalysisJob,
        CryptoFinding.job_id == AnalysisJob.id
    ).filter(
        AnalysisJob.client_id == client_id,
        CryptoFinding.pqc_compliant == False,
        CryptoFinding.risk_level.in_(['critical', 'high']),
        FindingControlMapping.confidence >= 0.7
    ).order_by(
        ComplianceFramework.code,
        CryptoFinding.risk_level
    ).all()

    return results

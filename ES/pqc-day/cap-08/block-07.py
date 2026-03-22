# Extraído de: LibroPQC/cap-08-certificados.md
def _calculate_pqc_readiness(self, findings: List[CertificateFinding]) -> float:
    """Score de preparación PQC basado en severidad de hallazgos"""
    if not findings:
        return 100.0

    weights = {
        'critical': 30,
        'high': 20,
        'medium': 10,
        'low': 5,
        'info': 1
    }
    total_penalty = sum(weights.get(f.severity, 0) for f in findings)
    return max(0, 100 - min(total_penalty, 100))

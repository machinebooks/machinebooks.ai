# Extraído de: LibroPQC/cap-10-owasp.md
# Ejemplo didáctico: analyzers/owasp_analyzer.py — resumen OWASP

def get_owasp_summary(self, findings: List[Dict]) -> Dict:
    """Genera resumen por categorías OWASP Top 10"""
    owasp_categories = {
        'A01': {'name': 'Broken Access Control', 'count': 0,
                'critical': 0, 'high': 0},
        'A02': {'name': 'Cryptographic Failures', 'count': 0,
                'critical': 0, 'high': 0},
        'A03': {'name': 'Injection', 'count': 0,
                'critical': 0, 'high': 0},
        # ... A04 a A10 con estructura idéntica
    }

    for finding in findings:
        owasp_id = finding.get('owasp_id', 'A00')
        if owasp_id in owasp_categories:
            owasp_categories[owasp_id]['count'] += 1
            severity = finding.get('severity', 'medium')
            if severity == 'critical':
                owasp_categories[owasp_id]['critical'] += 1
            elif severity == 'high':
                owasp_categories[owasp_id]['high'] += 1

    return owasp_categories

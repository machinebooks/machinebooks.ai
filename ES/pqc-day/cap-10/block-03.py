# Extraído de: LibroPQC/cap-10-owasp.md
# Ejemplo didáctico: analyzers/owasp_analyzer.py — análisis masivo

def analyze_files(self, files: List[Dict]) -> Dict:
    """Analiza múltiples ficheros y genera estadísticas agregadas"""
    all_findings = []
    files_with_issues = set()
    severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    category_counts = {}

    for file_info in files:
        file_path = file_info.get('path', '')
        content = file_info.get('content', '')

        findings = self.analyze_file_content(content, file_path)

        if findings:
            files_with_issues.add(file_path)
            all_findings.extend(findings)
            for finding in findings:
                sev = finding.get('severity', 'medium')
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
                cat = finding.get('owasp_category', 'Other')
                category_counts[cat] = category_counts.get(cat, 0) + 1

    return {
        'findings': all_findings,
        'total_findings': len(all_findings),
        'files_analyzed': len(files),
        'files_with_issues': len(files_with_issues),
        'severity_counts': severity_counts,
        'category_counts': category_counts,
    }

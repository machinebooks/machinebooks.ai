# Extraído de: LibroPQC/cap-09-auditoria-cloud.md
# Ejemplo didáctico: analyzers/cloud_security_analyzer.py

class CloudPQCAnalyzer:
    """Orquestador de análisis PQC multi-cloud"""

    def __init__(self):
        self.analyzers: Dict[str, CloudSecurityAnalyzer] = {}
        self.all_findings: List[SecurityFinding] = []

    def analyze_aws(self, connector, resource_types=None) -> Dict:
        """Ejecuta análisis PQC completo de AWS"""
        analyzer = CloudSecurityAnalyzer('aws')
        self.analyzers['aws'] = analyzer

        if resource_types is None:
            resource_types = ['kms', 's3', 'acm', 'iam']

        if 'kms' in resource_types:
            kms_keys = connector.get_kms_keys()
            analyzer.analyze_aws_kms(kms_keys)
        if 's3' in resource_types:
            buckets = connector.get_s3_buckets()
            analyzer.analyze_aws_s3_encryption(buckets)
        if 'acm' in resource_types:
            certs = connector.get_acm_certificates()
            analyzer.analyze_aws_acm_certificates(certs)

        self.all_findings.extend(analyzer.findings)
        return {'findings': analyzer.get_all_findings(),
                'summary': analyzer.get_summary()}

    def get_global_summary(self) -> Dict:
        """Resumen combinado de todos los proveedores"""
        return {
            'total_findings': len(self.all_findings),
            'provider_summaries': {
                name: a.get_summary()
                for name, a in self.analyzers.items()
            },
            'overall_pqc_readiness': self._calculate_overall_readiness()
        }

    def _calculate_overall_readiness(self) -> float:
        """Media de puntuaciones PQC de todos los proveedores"""
        if not self.analyzers:
            return 100.0
        scores = [a._calculate_pqc_readiness_score()
                  for a in self.analyzers.values()]
        return sum(scores) / len(scores)

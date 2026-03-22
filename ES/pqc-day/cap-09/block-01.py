# Extraído de: LibroPQC/cap-09-auditoria-cloud.md
# Ejemplo didáctico: analyzers/cloud_security_analyzer.py

@dataclass
class SecurityFinding:
    """Representa un hallazgo de seguridad con contexto PQC"""
    id: str
    provider: str
    resource_type: str          # 'KMS Key', 'S3 Bucket', 'ACM Certificate'
    resource_id: str
    resource_name: str
    severity: str               # critical, high, medium, low, info
    category: str               # 'Key Management', 'Data Protection', 'TLS/SSL'
    title: str
    description: str
    current_config: Dict[str, Any]  # configuración actual del recurso
    recommendation: str
    pqc_impact: str             # impacto específico post-cuántico
    remediation_steps: List[str]
    references: List[str]
    detected_at: str = None

    def __post_init__(self):
        if self.detected_at is None:
            self.detected_at = datetime.utcnow().isoformat()


class CloudSecurityAnalyzer:
    """Analiza configuraciones cloud para criptografía quantum-vulnerable"""

    def __init__(self, provider: str):
        self.provider = provider
        self.findings: List[SecurityFinding] = []
        self.finding_count = 0

    def _generate_finding_id(self) -> str:
        self.finding_count += 1
        return f"PQC-{self.provider.upper()}-{self.finding_count:04d}"

    def _check_algorithm_vulnerability(self, algorithm: str) -> Optional[Dict]:
        """Comprueba si un algoritmo es quantum-vulnerable"""
        algorithm_upper = algorithm.upper().replace('_', '-').replace(' ', '-')

        for category, algos in QUANTUM_VULNERABLE_ALGORITHMS.items():
            for algo_name, info in algos.items():
                if algo_name.upper() in algorithm_upper or \
                   algorithm_upper in algo_name.upper():
                    return {
                        'algorithm': algorithm,
                        'category': category,
                        'severity': info['severity'],
                        'reason': info['reason']
                    }
        return None

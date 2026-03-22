# Extraído de: LibroPQC/cap-09-auditoria-cloud.md
# Ejemplo didáctico: analyzers/cloud_scanner.py

class AWSCloudScanner:
    """Escáner de seguridad AWS con enfoque PQC"""

    def __init__(self, credentials: Dict[str, str],
                 regions: List[str] = None):
        self.credentials = credentials
        self.regions = regions or ['us-east-1', 'us-west-2', 'eu-west-1']
        self.findings: List[CloudFinding] = []
        self.resources_scanned = 0
        self.services_scanned = 0
        self.account_id = None

    def _get_session(self, region: str = 'us-east-1') -> boto3.Session:
        """Crea sesión boto3 con credenciales del cliente"""
        return boto3.Session(
            aws_access_key_id=self.credentials.get('access_key_id'),
            aws_secret_access_key=self.credentials.get('secret_access_key'),
            aws_session_token=self.credentials.get('session_token'),
            region_name=region
        )

    def _add_finding(self, rule_id: str, resource_id: str,
                    resource_arn: str, service: str,
                    resource_type: str, region: str,
                    metadata: Dict = None):
        """Añade un hallazgo basado en una regla del catálogo"""
        rule = AWS_PQC_RULES.get(rule_id)
        if not rule:
            return

        finding = CloudFinding(
            id=f"{rule_id}-{resource_id}",
            service=service,
            resource_type=resource_type,
            resource_id=resource_id,
            title=rule['title'],
            description=rule['description'],
            severity=rule['severity'],
            pqc_impact=rule['pqc_impact'],
            pqc_recommendation=rule['pqc_recommendation'],
            remediation=rule['remediation'],
            compliance=rule['compliance'],
            region=region,
            account_id=self._get_account_id(),
            resource_arn=resource_arn,
            metadata=metadata or {},
            discovered_at=datetime.utcnow().isoformat()
        )
        self.findings.append(finding)

# Extraído de: LibroPQC/cap-09-auditoria-cloud.md
# Ejemplo didáctico: analyzers/cloud_security_analyzer.py

def analyze_aws_s3_encryption(self, buckets: List[Dict]) -> List[SecurityFinding]:
    """Analiza configuración de cifrado de buckets S3"""
    findings = []

    for bucket in buckets:
        bucket_name = bucket.get('name', 'unknown')
        encryption = bucket.get('encryption', {})

        if not encryption or not encryption.get('enabled'):
            # Bucket sin cifrado: hallazgo de severidad alta
            findings.append(SecurityFinding(
                id=self._generate_finding_id(),
                provider='aws',
                resource_type='S3 Bucket',
                resource_id=bucket_name,
                resource_name=bucket_name,
                severity='high',
                category='Data Protection',
                title="S3 Bucket Without Default Encryption",
                description="Bucket sin cifrado por defecto habilitado",
                current_config={'encryption_enabled': False},
                recommendation="Enable default encryption with AES-256",
                pqc_impact="Unencrypted data is vulnerable to all attacks",
                remediation_steps=[
                    "Enable default encryption on the bucket",
                    "Use SSE-S3 with AES-256 or SSE-KMS",
                    "Audit existing objects for encryption status"
                ],
                references=[]
            ))
        else:
            sse_algorithm = encryption.get('sse_algorithm', '')
            # AES-128 tiene protección reducida post-cuántica
            if 'AES128' in sse_algorithm.upper():
                findings.append(SecurityFinding(
                    id=self._generate_finding_id(),
                    provider='aws',
                    resource_type='S3 Bucket',
                    resource_id=bucket_name,
                    resource_name=bucket_name,
                    severity='medium',
                    category='Data Protection',
                    title="S3 Bucket Using AES-128 Encryption",
                    description="AES-128 provides only 64-bit security "
                                "against quantum attacks (Grover's algorithm)",
                    current_config={'sse_algorithm': sse_algorithm},
                    recommendation="Upgrade to AES-256 encryption",
                    pqc_impact="Grover's algorithm reduces security margin",
                    remediation_steps=[
                        "Modify bucket encryption to use AES-256",
                        "Re-encrypt existing objects if necessary"
                    ],
                    references=[]
                ))

    self.findings.extend(findings)
    return findings

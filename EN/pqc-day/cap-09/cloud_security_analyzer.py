"""
PQC-Day and the Machine — Chapter 9
Pattern: CloudSecurityAnalyzer — classify cloud resources by quantum vulnerability

This is a didactic example from the book, not production code.
See chapter 9 for full context and explanation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional

from quantum_vulnerable_algorithms import QUANTUM_VULNERABLE_ALGORITHMS


@dataclass
class SecurityFinding:
    """Represents a security finding with PQC context."""
    id: str
    provider: str
    resource_type: str          # 'KMS Key', 'S3 Bucket', 'ACM Certificate'
    resource_id: str
    resource_name: str
    severity: str               # critical, high, medium, low, info
    category: str               # 'Key Management', 'Data Protection', 'TLS/SSL'
    title: str
    description: str
    current_config: Dict[str, Any]
    recommendation: str
    pqc_impact: str
    remediation_steps: List[str]
    references: List[str]
    detected_at: str = None

    def __post_init__(self):
        if self.detected_at is None:
            self.detected_at = datetime.utcnow().isoformat()


class CloudSecurityAnalyzer:
    """Analyzes cloud configurations for quantum-vulnerable cryptography."""

    def __init__(self, provider: str):
        self.provider = provider
        self.findings: List[SecurityFinding] = []
        self.finding_count = 0

    def _generate_finding_id(self) -> str:
        self.finding_count += 1
        return f"PQC-{self.provider.upper()}-{self.finding_count:04d}"

    def _check_algorithm_vulnerability(self, algorithm: str) -> Optional[Dict]:
        """Check if an algorithm is quantum-vulnerable."""
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

    def analyze_aws_kms(self, kms_keys: List[Dict]) -> List[SecurityFinding]:
        """Analyze AWS KMS keys for quantum vulnerabilities."""
        findings = []

        for key in kms_keys:
            key_spec = key.get('key_spec', '')
            key_id = key.get('key_id', 'unknown')
            key_arn = key.get('arn', '')

            # Check the KeySpec
            vuln = self._check_algorithm_vulnerability(key_spec)
            if vuln:
                finding = SecurityFinding(
                    id=self._generate_finding_id(),
                    provider='aws',
                    resource_type='KMS Key',
                    resource_id=key_id,
                    resource_name=key_arn,
                    severity=vuln['severity'],
                    category='Key Management',
                    title=f"Quantum-Vulnerable KMS Key: {key_spec}",
                    description=f"KMS key uses {key_spec} which is {vuln['reason']}",
                    current_config={
                        'key_spec': key_spec,
                        'key_usage': key.get('key_usage')
                    },
                    recommendation="Plan migration to post-quantum key algorithms",
                    pqc_impact="Data encrypted with this key may be decrypted "
                               "by quantum computers",
                    remediation_steps=[
                        "Inventory all resources using this KMS key",
                        "Monitor AWS announcements for PQC KMS support",
                        "Prepare migration plan to hybrid or PQC keys",
                        "Consider additional symmetric encryption layer"
                    ],
                    references=[
                        "https://aws.amazon.com/security/post-quantum-cryptography/"
                    ]
                )
                findings.append(finding)

            # Check each supported encryption algorithm
            for enc_algo in key.get('encryption_algorithms', []):
                vuln = self._check_algorithm_vulnerability(enc_algo)
                if vuln:
                    findings.append(SecurityFinding(
                        id=self._generate_finding_id(),
                        provider='aws',
                        resource_type='KMS Key Encryption Algorithm',
                        resource_id=key_id,
                        resource_name=key_arn,
                        severity=vuln['severity'],
                        category='Encryption',
                        title=f"Quantum-Vulnerable Encryption: {enc_algo}",
                        description=f"KMS key supports {enc_algo} which is "
                                    f"{vuln['reason']}",
                        current_config={'encryption_algorithm': enc_algo},
                        recommendation="Disable vulnerable encryption algorithms",
                        pqc_impact="Encrypted data may be harvested now and "
                                   "decrypted later",
                        remediation_steps=[
                            "Audit usage of this encryption algorithm",
                            "Transition to symmetric encryption where possible"
                        ],
                        references=["https://csrc.nist.gov/projects/post-quantum-cryptography"]
                    ))

            # Check signing algorithms
            for sign_algo in key.get('signing_algorithms', []):
                vuln = self._check_algorithm_vulnerability(sign_algo)
                if vuln:
                    findings.append(SecurityFinding(
                        id=self._generate_finding_id(),
                        provider='aws',
                        resource_type='KMS Key Signing Algorithm',
                        resource_id=key_id,
                        resource_name=key_arn,
                        severity=vuln['severity'],
                        category='Digital Signatures',
                        title=f"Quantum-Vulnerable Signing: {sign_algo}",
                        description=f"KMS key supports {sign_algo} signing",
                        current_config={'signing_algorithm': sign_algo},
                        recommendation="Prepare migration to post-quantum signatures",
                        pqc_impact="Signatures may be forged by quantum computers",
                        remediation_steps=[
                            "Identify all signature verification points",
                            "Plan migration to hybrid signatures",
                            "Consider hash-based signatures for long-term documents"
                        ],
                        references=["https://csrc.nist.gov/projects/post-quantum-cryptography"]
                    ))

        self.findings.extend(findings)
        return findings

    def analyze_aws_s3_encryption(self, buckets: List[Dict]) -> List[SecurityFinding]:
        """Analyze S3 bucket encryption configuration."""
        findings = []

        for bucket in buckets:
            bucket_name = bucket.get('name', 'unknown')
            encryption = bucket.get('encryption', {})

            if not encryption or not encryption.get('enabled'):
                findings.append(SecurityFinding(
                    id=self._generate_finding_id(),
                    provider='aws',
                    resource_type='S3 Bucket',
                    resource_id=bucket_name,
                    resource_name=bucket_name,
                    severity='high',
                    category='Data Protection',
                    title="S3 Bucket Without Default Encryption",
                    description="Bucket has no default encryption enabled",
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

    def get_summary(self) -> Dict:
        """Generate summary of all findings."""
        severity_counts = {}
        for f in self.findings:
            severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1

        return {
            'provider': self.provider,
            'total_findings': len(self.findings),
            'severity_counts': severity_counts,
            'categories': list(set(f.category for f in self.findings)),
        }


# --- Main ---
if __name__ == '__main__':
    # Example: analyze sample AWS resources
    analyzer = CloudSecurityAnalyzer(provider='aws')

    # Sample KMS keys
    sample_keys = [
        {
            'key_id': 'key-001',
            'arn': 'arn:aws:kms:eu-west-1:123456:key/key-001',
            'key_spec': 'RSA_2048',
            'key_usage': 'SIGN_VERIFY',
            'encryption_algorithms': ['RSAES_OAEP_SHA_256'],
            'signing_algorithms': ['RSASSA_PSS_SHA_256'],
        },
        {
            'key_id': 'key-002',
            'arn': 'arn:aws:kms:eu-west-1:123456:key/key-002',
            'key_spec': 'SYMMETRIC_DEFAULT',
            'key_usage': 'ENCRYPT_DECRYPT',
            'encryption_algorithms': ['SYMMETRIC_DEFAULT'],
            'signing_algorithms': [],
        },
    ]

    # Sample S3 buckets
    sample_buckets = [
        {'name': 'data-lake', 'encryption': {'enabled': True, 'sse_algorithm': 'AES256'}},
        {'name': 'logs-bucket', 'encryption': {'enabled': False}},
        {'name': 'temp-data', 'encryption': {'enabled': True, 'sse_algorithm': 'AES128'}},
    ]

    kms_findings = analyzer.analyze_aws_kms(sample_keys)
    s3_findings = analyzer.analyze_aws_s3_encryption(sample_buckets)
    summary = analyzer.get_summary()

    print(f"Provider: {summary['provider']}")
    print(f"Total findings: {summary['total_findings']}")
    print(f"Severity: {summary['severity_counts']}")

    for f in analyzer.findings:
        print(f"\n[{f.severity.upper():8s}] {f.title}")
        print(f"  Resource: {f.resource_name}")
        print(f"  Impact: {f.pqc_impact}")
        print(f"  Recommendation: {f.recommendation}")

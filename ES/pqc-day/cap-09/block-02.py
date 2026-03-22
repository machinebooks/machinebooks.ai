# Extraído de: LibroPQC/cap-09-auditoria-cloud.md
# Ejemplo didáctico: analyzers/cloud_security_analyzer.py

def analyze_aws_kms(self, kms_keys: List[Dict]) -> List[SecurityFinding]:
    """Analiza claves AWS KMS para vulnerabilidades cuánticas"""
    findings = []

    for key in kms_keys:
        key_spec = key.get('key_spec', '')     # RSA_2048, ECC_NIST_P256, SYMMETRIC_DEFAULT
        key_id = key.get('key_id', 'unknown')
        key_arn = key.get('arn', '')

        # Comprobar el KeySpec — el tipo de clave es lo primero
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

        # Comprobar cada algoritmo de cifrado soportado
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

        # Comprobar algoritmos de firma
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

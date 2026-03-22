# Extraído de: LibroPQC/cap-09-auditoria-cloud.md
# Ejemplo didáctico: analyzers/cloud_security_analyzer.py

def analyze_azure_key_vault(self, keys: List[Dict]) -> List[SecurityFinding]:
    """Analiza claves Azure Key Vault para vulnerabilidades cuánticas"""
    findings = []

    for key in keys:
        key_name = key.get('name', 'unknown')
        key_type = key.get('key_type', '')    # RSA, EC, oct
        key_size = key.get('key_size', 0)
        curve_name = key.get('curve_name', '')

        if 'RSA' in key_type.upper():
            findings.append(SecurityFinding(
                id=self._generate_finding_id(),
                provider='azure',
                resource_type='Key Vault Key',
                resource_id=key_name,
                resource_name=key_name,
                severity='critical',
                category='Key Management',
                title=f"Quantum-Vulnerable RSA Key in Key Vault",
                description=f"Key uses RSA-{key_size} which is vulnerable "
                            f"to Shor's algorithm",
                current_config={'key_type': key_type, 'key_size': key_size},
                recommendation="Plan migration to PQC algorithms when "
                              "Azure supports them",
                pqc_impact="Private key may be derived using quantum computers",
                remediation_steps=[
                    "Inventory all applications using this key",
                    "Implement additional symmetric encryption",
                    "Monitor Azure announcements for PQC Key Vault support"
                ],
                references=[]
            ))

        elif 'EC' in key_type.upper():
            findings.append(SecurityFinding(
                id=self._generate_finding_id(),
                provider='azure',
                resource_type='Key Vault Key',
                resource_id=key_name,
                resource_name=key_name,
                severity='critical',
                category='Key Management',
                title=f"Quantum-Vulnerable EC Key in Key Vault",
                description=f"Key uses EC curve {curve_name} which is "
                            f"vulnerable to Shor's algorithm",
                current_config={'key_type': key_type, 'curve': curve_name},
                recommendation="Plan migration to PQC algorithms",
                pqc_impact="Private key may be derived using quantum computers",
                remediation_steps=[
                    "Transition to symmetric encryption where possible",
                    "Monitor for PQC support in Azure Key Vault"
                ],
                references=[]
            ))

    self.findings.extend(findings)
    return findings

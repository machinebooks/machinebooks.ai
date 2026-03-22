# Extraído de: LibroPQC/cap-09-auditoria-cloud.md
# Ejemplo didáctico: analyzers/cloud_scanner.py

AWS_PQC_RULES = {
    # S3 - Protección de datos almacenados
    's3-bucket-not-encrypted': {
        'severity': 'high',
        'pqc_impact': 'high',  # ← específico PQC
        'title': 'S3 Bucket Not Encrypted',
        'description': 'S3 bucket does not have server-side encryption',
        'pqc_recommendation': 'Enable AES-256 encryption. '  # ← específico PQC
                             'Plan migration to PQC-safe encryption '
                             'when AWS supports it.',
        'remediation': 'Enable default encryption with SSE-S3 or SSE-KMS',
        'compliance': ['CIS AWS 2.1.1', 'NIST 800-53 SC-28']
    },

    # KMS - Gestión de claves (crítico para PQC)
    'kms-key-rotation-disabled': {
        'severity': 'high',
        'pqc_impact': 'critical',  # ← más grave en contexto PQC
        'title': 'KMS Key Rotation Disabled',
        'description': 'KMS customer-managed key does not have automatic '
                      'rotation enabled',
        'pqc_recommendation': 'Enable key rotation to prepare for PQC '
                             'algorithm migration. Frequent rotation reduces '
                             'harvest-now-decrypt-later exposure.',
        'remediation': 'Enable automatic key rotation for the CMK',
        'compliance': ['CIS AWS 2.8', 'NIST 800-53 SC-12']
    },

    # RDS - Bases de datos
    'rds-ssl-not-enforced': {
        'severity': 'high',
        'pqc_impact': 'critical',
        'title': 'RDS SSL/TLS Not Enforced',
        'description': 'RDS instance does not enforce SSL/TLS for connections',
        'pqc_recommendation': 'Enforce TLS 1.2+. SSL/TLS traffic is '
                             'quantum-vulnerable. Monitor for PQC-TLS support.',
        'remediation': 'Enable SSL/TLS enforcement via parameter groups',
        'compliance': ['NIST 800-53 SC-8']
    },

    # ACM - Certificados (muy relevante para PQC)
    'acm-certificate-rsa-key-size': {
        'severity': 'high',
        'pqc_impact': 'critical',
        'title': 'ACM Certificate Uses RSA Key',
        'description': 'ACM certificate uses RSA key (any size)',
        'pqc_recommendation': 'ALL RSA keys are quantum-vulnerable. '
                             'Plan PQC migration.',
        'remediation': 'Request new certificate with RSA-2048+ or ECDSA',
        'compliance': ['NIST 800-53 SC-12']
    },
    # ... 20+ reglas adicionales para EC2, IAM, CloudTrail,
    #     Lambda, ELB, DynamoDB, EFS, Redshift, API Gateway
}

# Extraído de: LibroPQC/cap-15-nis2.md
class ComplianceService:
    """Servicio principal para operaciones de compliance"""

    # Mapeo determinístico: categorías de hallazgos → controles
    FINDING_TO_CONTROL_MAPPING = {
        'crypto': {
            'keywords': ['rsa', 'aes', 'des', 'md5', 'sha1', 'encryption',
                         'cipher', 'key', 'certificate', 'ssl', 'tls'],
            'controls': ['NIS2.RISK.8'],     # Criptografía y cifrado
            'domain': 'Criptografía'
        },
        'weak_crypto': {
            'keywords': ['weak', 'deprecated', 'vulnerable', 'insecure'],
            'controls': ['NIS2.RISK.8'],
            'impact': 'violation'            # Incumplimiento directo
        },
        'quantum': {
            'keywords': ['quantum', 'post-quantum', 'pqc', 'lattice',
                         'kyber', 'dilithium'],
            'controls': ['NIS2.RISK.8', 'NIS2.RISK.1'],
            'domain': 'Criptografía Post-Cuántica'
        },
        'access_control': {
            'keywords': ['access', 'authentication', 'authorization',
                         'mfa', 'password', 'credential'],
            'controls': ['NIS2.RISK.9', 'NIS2.RISK.10'],
            'domain': 'Control de Acceso'
        },
        'supply_chain': {
            'keywords': ['dependency', 'third-party', 'library',
                         'package', 'vendor'],
            'controls': ['NIS2.RISK.4'],
            'domain': 'Cadena de Suministro'
        },
    }

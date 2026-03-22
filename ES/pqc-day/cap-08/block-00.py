# Extraído de: LibroPQC/cap-08-certificados.md
TLS_VERSION_SECURITY = {
    'TLSv1.3': {
        'severity': 'info',
        'secure': True,
        'note': 'Most secure, still uses quantum-vulnerable key exchange'
    },
    'TLSv1.2': {
        'severity': 'low',
        'secure': True,
        'note': 'Secure but may use vulnerable ciphers'
    },
    'TLSv1.1': {
        'severity': 'high',
        'secure': False,
        'note': 'Deprecated, should not be used'
    },
    'TLSv1.0': {
        'severity': 'high',
        'secure': False,
        'note': 'Deprecated, known vulnerabilities'
    },
    'SSLv3': {
        'severity': 'critical',
        'secure': False,
        'note': 'POODLE vulnerability, must disable'
    },
    'SSLv2': {
        'severity': 'critical',
        'secure': False,
        'note': 'Completely broken, must disable'
    },
}

# Extraído de: LibroPQC/cap-17-nist-pqc.md
# Ejemplo didáctico: analyzers/cloud_security_analyzer.py

QUANTUM_VULNERABILITY_PROFILE = {
    # Criptografía asimétrica: Shor la destruye
    'asymmetric': {
        'RSA': {'severity': 'critical',
                'reason': 'Shor factoriza la clave en tiempo polinómico'},
        'ECDSA': {'severity': 'critical',
                  'reason': 'Shor resuelve logaritmo discreto en curvas'},
        'ECDH': {'severity': 'critical',
                 'reason': 'Intercambio de claves vulnerable a Shor'},
        'DH': {'severity': 'critical',
               'reason': 'Diffie-Hellman vulnerable a Shor'},
        'DSA': {'severity': 'critical',
                'reason': 'Logaritmo discreto vulnerable a Shor'},
        'ElGamal': {'severity': 'critical',
                    'reason': 'Logaritmo discreto vulnerable a Shor'},
    },
    # Hashes: Grover los debilita, no los rompe
    'hash': {
        'MD5': {'severity': 'high',
                'reason': 'Roto clásicamente + debilitado por Grover'},
        'SHA-1': {'severity': 'high',
                  'reason': 'Colisiones demostradas + debilitado por Grover'},
        'SHA-256': {'severity': 'low',
                    'reason': 'Grover reduce a 128 bits; sigue seguro'},
        'SHA-384': {'severity': 'info',
                    'reason': '192 bits efectivos post-Grover'},
        'SHA-512': {'severity': 'info',
                    'reason': '256 bits efectivos post-Grover'},
    },
    # Cipher suites TLS: el componente más débil define el riesgo
    'tls_ciphers': {
        'TLS_RSA_WITH_': {'severity': 'critical',
                          'reason': 'RSA key exchange quantum vulnerable'},
        'TLS_ECDHE_RSA_': {'severity': 'critical',
                           'reason': 'ECDHE+RSA ambos quantum vulnerable'},
        'TLS_AES_256_': {'severity': 'info',
                         'reason': 'AES-256 seguro post-cuántico'},
        'TLS_CHACHA20_': {'severity': 'info',
                          'reason': 'ChaCha20 seguro post-cuántico'},
    },
}

# Extraído de: LibroPQC/cap-09-auditoria-cloud.md
# Ejemplo didáctico: analyzers/cloud_security_analyzer.py

QUANTUM_VULNERABLE_ALGORITHMS = {
    # Algoritmos asimétricos vulnerables al algoritmo de Shor
    'asymmetric': {
        'RSA': {'severity': 'critical', 'reason': 'Vulnerable to Shor\'s algorithm'},
        'RSA-2048': {'severity': 'critical', 'reason': 'Vulnerable to Shor\'s algorithm'},
        'RSA-4096': {'severity': 'critical', 'reason': 'Vulnerable to Shor\'s algorithm'},
        'ECDSA': {'severity': 'critical', 'reason': 'Vulnerable to Shor\'s algorithm'},
        'ECDH': {'severity': 'critical', 'reason': 'Vulnerable to Shor\'s algorithm'},
        'Ed25519': {'severity': 'critical', 'reason': 'EdDSA vulnerable to Shor\'s algorithm'},
        'X25519': {'severity': 'critical', 'reason': 'ECDH vulnerable to Shor\'s algorithm'},
        'P-256': {'severity': 'critical', 'reason': 'NIST P-256 vulnerable to Shor\'s'},
        'P-384': {'severity': 'critical', 'reason': 'NIST P-384 vulnerable to Shor\'s'},
        # ... 15+ entradas adicionales
    },
    # Simétricos: necesitan claves más largas para resistencia cuántica
    'symmetric': {
        'AES-128': {'severity': 'medium', 'reason': 'Grover reduces security to 64-bit'},
        'AES-256': {'severity': 'info', 'reason': 'Still secure with 128-bit post-quantum'},
        'DES': {'severity': 'critical', 'reason': 'Deprecated + trivially broken'},
        '3DES': {'severity': 'high', 'reason': 'Weak + Grover reduces security'},
        'RC4': {'severity': 'critical', 'reason': 'Deprecated + known vulnerabilities'},
    },
    # Funciones hash
    'hash': {
        'MD5': {'severity': 'critical', 'reason': 'Broken + collision attacks'},
        'SHA-1': {'severity': 'high', 'reason': 'Deprecated + collision attacks'},
        'SHA-256': {'severity': 'low', 'reason': 'Grover reduces to 128-bit security'},
        'SHA-384': {'severity': 'info', 'reason': 'Still secure post-quantum'},
    },
    # Suites TLS/SSL
    'tls_ciphers': {
        'TLS_RSA_WITH_': {'severity': 'critical', 'reason': 'RSA key exchange vulnerable'},
        'TLS_ECDHE_RSA_': {'severity': 'critical', 'reason': 'ECDHE+RSA vulnerable'},
        'TLS_AES_256_': {'severity': 'info', 'reason': 'AES-256 still secure post-quantum'},
    }
}

# Contrapartida: algoritmos PQC-safe (NIST aprobados)
PQC_SAFE_ALGORITHMS = {
    'key_encapsulation': ['ML-KEM', 'CRYSTALS-Kyber', 'Kyber-768', 'Kyber-1024'],
    'digital_signatures': ['ML-DSA', 'CRYSTALS-Dilithium', 'SLH-DSA', 'SPHINCS+',
                          'FALCON', 'Falcon-512', 'Falcon-1024'],
    'symmetric': ['AES-256', 'AES-256-GCM', 'ChaCha20-Poly1305'],
    'hash': ['SHA-384', 'SHA-512', 'SHA3-256', 'SHA3-512'],
}

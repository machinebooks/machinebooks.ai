"""
PQC-Day and the Machine — Chapter 9
Pattern: Quantum-vulnerable algorithm classification dictionary

This is a didactic example from the book, not production code.
See chapter 9 for full context and explanation.
"""

# Classification of algorithms by quantum vulnerability.
# Used across all analysis engines of the PQC Platform.

QUANTUM_VULNERABLE_ALGORITHMS = {
    # Asymmetric algorithms vulnerable to Shor's algorithm
    'asymmetric': {
        'RSA': {'severity': 'critical', 'reason': "Vulnerable to Shor's algorithm"},
        'RSA-2048': {'severity': 'critical', 'reason': "Vulnerable to Shor's algorithm"},
        'RSA-4096': {'severity': 'critical', 'reason': "Vulnerable to Shor's algorithm"},
        'ECDSA': {'severity': 'critical', 'reason': "Vulnerable to Shor's algorithm"},
        'ECDH': {'severity': 'critical', 'reason': "Vulnerable to Shor's algorithm"},
        'Ed25519': {'severity': 'critical', 'reason': "EdDSA vulnerable to Shor's algorithm"},
        'X25519': {'severity': 'critical', 'reason': "ECDH vulnerable to Shor's algorithm"},
        'P-256': {'severity': 'critical', 'reason': "NIST P-256 vulnerable to Shor's"},
        'P-384': {'severity': 'critical', 'reason': "NIST P-384 vulnerable to Shor's"},
    },
    # Symmetric: need longer keys for quantum resistance
    'symmetric': {
        'AES-128': {'severity': 'medium', 'reason': "Grover reduces security to 64-bit"},
        'AES-256': {'severity': 'info', 'reason': 'Still secure with 128-bit post-quantum'},
        'DES': {'severity': 'critical', 'reason': 'Deprecated + trivially broken'},
        '3DES': {'severity': 'high', 'reason': 'Weak + Grover reduces security'},
        'RC4': {'severity': 'critical', 'reason': 'Deprecated + known vulnerabilities'},
    },
    # Hash functions
    'hash': {
        'MD5': {'severity': 'critical', 'reason': 'Broken + collision attacks'},
        'SHA-1': {'severity': 'high', 'reason': 'Deprecated + collision attacks'},
        'SHA-256': {'severity': 'low', 'reason': 'Grover reduces to 128-bit security'},
        'SHA-384': {'severity': 'info', 'reason': 'Still secure post-quantum'},
    },
    # TLS/SSL suites
    'tls_ciphers': {
        'TLS_RSA_WITH_': {'severity': 'critical', 'reason': 'RSA key exchange vulnerable'},
        'TLS_ECDHE_RSA_': {'severity': 'critical', 'reason': 'ECDHE+RSA vulnerable'},
        'TLS_AES_256_': {'severity': 'info', 'reason': 'AES-256 still secure post-quantum'},
    }
}

# Counterpart: PQC-safe algorithms (NIST approved)
PQC_SAFE_ALGORITHMS = {
    'key_encapsulation': ['ML-KEM', 'CRYSTALS-Kyber', 'Kyber-768', 'Kyber-1024'],
    'digital_signatures': ['ML-DSA', 'CRYSTALS-Dilithium', 'SLH-DSA', 'SPHINCS+',
                          'FALCON', 'Falcon-512', 'Falcon-1024'],
    'symmetric': ['AES-256', 'AES-256-GCM', 'ChaCha20-Poly1305'],
    'hash': ['SHA-384', 'SHA-512', 'SHA3-256', 'SHA3-512'],
}


if __name__ == '__main__':
    print("=== Quantum-Vulnerable Algorithms ===\n")
    for category, algos in QUANTUM_VULNERABLE_ALGORITHMS.items():
        print(f"\n{category.upper()}:")
        for name, info in algos.items():
            print(f"  [{info['severity']:8s}] {name:15s} — {info['reason']}")

    print("\n\n=== PQC-Safe Algorithms (NIST Approved) ===\n")
    for category, algos in PQC_SAFE_ALGORITHMS.items():
        print(f"  {category}: {', '.join(algos)}")

# Extraído de: LibroPQC/cap-08-certificados.md
CIPHER_SUITE_ANALYSIS = {
    # Intercambio de claves — todos vulnerables a Shor
    'RSA':   {'type': 'key_exchange', 'quantum_vulnerable': True,
              'severity': 'critical',
              'reason': 'RSA key exchange vulnerable to Shor\'s algorithm'},
    'DHE':   {'type': 'key_exchange', 'quantum_vulnerable': True,
              'severity': 'critical',
              'reason': 'DHE vulnerable to Shor\'s algorithm'},
    'ECDHE': {'type': 'key_exchange', 'quantum_vulnerable': True,
              'severity': 'critical',
              'reason': 'ECDHE vulnerable to Shor\'s algorithm'},

    # Autenticación — vulnerables a Shor
    'RSA_SIGN': {'type': 'authentication', 'quantum_vulnerable': True,
                 'severity': 'critical',
                 'reason': 'RSA signatures vulnerable to Shor\'s algorithm'},
    'ECDSA':    {'type': 'authentication', 'quantum_vulnerable': True,
                 'severity': 'critical',
                 'reason': 'ECDSA signatures vulnerable to Shor\'s algorithm'},

    # Cifrado simétrico — quantum-safe con matices
    'AES_128_GCM': {'type': 'symmetric', 'quantum_vulnerable': False,
                    'severity': 'medium',
                    'reason': 'Grover\'s reduces to 64-bit, but still acceptable'},
    'AES_256_GCM': {'type': 'symmetric', 'quantum_vulnerable': False,
                    'severity': 'info',
                    'reason': 'Strong symmetric cipher, quantum-safe'},
    'CHACHA20':    {'type': 'symmetric', 'quantum_vulnerable': False,
                    'severity': 'info',
                    'reason': 'ChaCha20-Poly1305 is quantum-resistant'},
    '3DES':        {'type': 'symmetric', 'quantum_vulnerable': False,
                    'severity': 'high',
                    'reason': 'Deprecated, 64-bit block size sweet32 attack'},
    'RC4':         {'type': 'symmetric', 'quantum_vulnerable': False,
                    'severity': 'critical',
                    'reason': 'Stream cipher with known biases, must not use'},

    # Hashes
    'SHA256': {'type': 'hash', 'quantum_vulnerable': False,
               'severity': 'low',
               'reason': 'SHA-256 provides 128-bit post-quantum security'},
    'SHA384': {'type': 'hash', 'quantum_vulnerable': False,
               'severity': 'info',
               'reason': 'SHA-384 is quantum-resistant'},
    'MD5':    {'type': 'hash', 'quantum_vulnerable': False,
               'severity': 'critical',
               'reason': 'MD5 is completely broken'},
}

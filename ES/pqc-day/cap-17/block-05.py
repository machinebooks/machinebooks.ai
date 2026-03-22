# Extraído de: LibroPQC/cap-17-nist-pqc.md
# Ejemplo didáctico: analyzers/url_certificate_scanner.py

PQC_SUPPORTED_GROUPS = {
    # ML-KEM puro (FIPS 203)
    512: {'name': 'MLKEM512', 'type': 'pure_pqc', 'security_level': 1},
    513: {'name': 'MLKEM768', 'type': 'pure_pqc', 'security_level': 3},
    514: {'name': 'MLKEM1024', 'type': 'pure_pqc', 'security_level': 5},

    # Híbridos (clásico + ML-KEM)
    4587: {'name': 'SecP256r1MLKEM768', 'type': 'hybrid',
           'security_level': 3},
    4588: {'name': 'X25519MLKEM768', 'type': 'hybrid',
           'security_level': 3},  # Más desplegado actualmente
    4589: {'name': 'SecP384r1MLKEM1024', 'type': 'hybrid',
           'security_level': 5},

    # Legacy Kyber (pre-ML-KEM, todavía usado en transición)
    25497: {'name': 'X25519Kyber768Draft00', 'type': 'hybrid_legacy',
            'security_level': 3},
    25498: {'name': 'SecP256r1Kyber768Draft00', 'type': 'hybrid_legacy',
            'security_level': 3},
}

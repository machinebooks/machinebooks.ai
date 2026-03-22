# Extraído de: LibroPQC/cap-08-certificados.md
PQC_SUPPORTED_GROUPS = {
    # ML-KEM puro (FIPS 203)
    512: {'name': 'MLKEM512',  'type': 'pure_pqc', 'security_level': 1},
    513: {'name': 'MLKEM768',  'type': 'pure_pqc', 'security_level': 3},
    514: {'name': 'MLKEM1024', 'type': 'pure_pqc', 'security_level': 5},

    # Combinaciones híbridas (recomendadas para la transición)
    4587: {'name': 'SecP256r1MLKEM768',  'type': 'hybrid', 'security_level': 3},
    4588: {'name': 'X25519MLKEM768',     'type': 'hybrid', 'security_level': 3},
    4589: {'name': 'SecP384r1MLKEM1024', 'type': 'hybrid', 'security_level': 5},

    # Kyber legacy (pre-ML-KEM, aún en uso durante la transición)
    25497: {'name': 'X25519Kyber768Draft00',    'type': 'hybrid_legacy',
            'security_level': 3},
    25498: {'name': 'SecP256r1Kyber768Draft00',  'type': 'hybrid_legacy',
            'security_level': 3},
}

# Grupos clásicos de intercambio de claves (quantum-vulnerable)
CLASSICAL_KEY_EXCHANGE_GROUPS = {
    23:  'secp256r1 (P-256)',
    24:  'secp384r1 (P-384)',
    25:  'secp521r1 (P-521)',
    29:  'x25519',
    30:  'x448',
    256: 'ffdhe2048',
    257: 'ffdhe3072',
    258: 'ffdhe4096',
}

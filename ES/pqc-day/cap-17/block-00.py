# Extraído de: LibroPQC/cap-17-nist-pqc.md
# Ejemplo didáctico: analyzers/cloud_security_analyzer.py

# PQC-Safe algorithms (NIST approved)
PQC_SAFE_ALGORITHMS = {
    'key_encapsulation': [
        'ML-KEM',              # FIPS 203
        'CRYSTALS-Kyber',      # Nombre pre-estandarización
        'Kyber-512',           # Nivel de seguridad 1
        'Kyber-768',           # Nivel de seguridad 3 (recomendado)
        'Kyber-1024',          # Nivel de seguridad 5
    ],
    'digital_signatures': [
        'ML-DSA',              # FIPS 204
        'CRYSTALS-Dilithium',  # Nombre pre-estandarización
        'Dilithium2',          # ML-DSA-44 (nivel 2)
        'Dilithium3',          # ML-DSA-65 (nivel 3)
        'Dilithium5',          # ML-DSA-87 (nivel 5)
        'FALCON',              # FN-DSA (en estandarización)
        'Falcon-512',          # Firma compacta nivel 1
        'Falcon-1024',         # Firma compacta nivel 5
        'SLH-DSA',             # FIPS 205
        'SPHINCS+',            # Nombre pre-estandarización
    ],
    'symmetric': [
        'AES-256',             # Seguro post-cuántico (128 bits efect.)
        'AES-256-GCM',         # Modo autenticado preferido
        'ChaCha20-Poly1305',   # Alternativa a AES-GCM
    ],
    'hash': [
        'SHA-384',             # 192 bits efectivos post-Grover
        'SHA-512',             # 256 bits efectivos post-Grover
        'SHA3-256',            # Familia Keccak, resistente
        'SHA3-384',
        'SHA3-512',
        'SHAKE128',            # Funciones extensibles (usadas por ML-DSA)
        'SHAKE256',
    ],
}

# Extraído de: LibroPQC/cap-07-analisis-codigo.md
def _get_recommendation(self, algorithm: str) -> str:
    """Recomendación de migración basada en el algoritmo"""
    recommendations = {
        'RSA': 'Migrar a ML-KEM (Kyber) para cifrado o ML-DSA (Dilithium) para firmas',
        'DSA': 'Reemplazar por ML-DSA (Dilithium) o SLH-DSA (SPHINCS+)',
        'ECDSA': 'Reemplazar por ML-DSA (Dilithium) o SLH-DSA (SPHINCS+)',
        'ECC': 'Reemplazar por ML-KEM (Kyber) para intercambio de claves',
        'ECDH': 'Reemplazar por ML-KEM (Kyber) para encapsulación de claves',
        'DH': 'Reemplazar por ML-KEM (Kyber) para encapsulación de claves',
        'DES': 'Reemplazar inmediatamente por AES-256-GCM',
        '3DES': 'Reemplazar por AES-256-GCM',
        'MD5': 'Reemplazar por SHA-384 o SHA3-256',
        'SHA-1': 'Reemplazar por SHA-384 o SHA3-256',
        'AES-128': 'Actualizar a AES-256 para margen post-cuántico',
        'RSA-JWT': 'Preparar migración a JWT híbrido o PQC-JWT cuando se estandarice',
        'ECDSA-JWT': 'Preparar migración a JWT híbrido o PQC-JWT cuando se estandarice',
    }
    return recommendations.get(algorithm, 'Evaluar y migrar a alternativa post-cuántica')

# Extraído de: LibroPQC/cap-17-nist-pqc.md
# Ejemplo didáctico: analyzers/repository_analyzer.py

def _get_recommendation(self, algorithm: str) -> str:
    """Genera recomendación de migración basada en estándar NIST."""
    recommendations = {
        # Intercambio de claves -> FIPS 203 (ML-KEM)
        'RSA': (
            'Migrar a ML-KEM (FIPS 203) para encapsulación de claves '
            'o a ML-DSA (FIPS 204) para firmas digitales'
        ),
        'ECDH': 'Reemplazar con ML-KEM (FIPS 203) para encapsulación de claves',
        'DH': 'Reemplazar con ML-KEM (FIPS 203) para encapsulación de claves',
        'X25519': 'Reemplazar con ML-KEM (FIPS 203) para intercambio de claves',

        # Firmas digitales -> FIPS 204 (ML-DSA) o FIPS 205 (SLH-DSA)
        'ECDSA': (
            'Reemplazar con ML-DSA (FIPS 204) o SLH-DSA (FIPS 205) '
            'para firmas digitales'
        ),
        'DSA': (
            'Reemplazar con ML-DSA (FIPS 204) o SLH-DSA (FIPS 205) '
            'para firmas digitales'
        ),
        'ECC': (
            'Reemplazar con ML-KEM (FIPS 203) para intercambio de claves '
            'o ML-DSA (FIPS 204) para firmas'
        ),
        'Ed25519': (
            'Reemplazar con ML-DSA (FIPS 204) o considerar firmas '
            'basadas en hash (FIPS 205)'
        ),

        # Criptografía simétrica débil (no PQC, pero sí urgente)
        'DES': 'Reemplazar inmediatamente con AES-256-GCM',
        '3DES': 'Reemplazar con AES-256-GCM',

        # Hash débil
        'MD5': 'Reemplazar con SHA-384 o SHA3-256',
        'SHA-1': 'Reemplazar con SHA-384 o SHA3-256',

        # JWT (sin estándar PQC final todavía)
        'RSA-JWT': (
            'Migrar a esquema híbrido JWT o preparar para PQC JWT '
            'cuando se estandarice (IETF draft en progreso)'
        ),
        'ECDSA-JWT': (
            'Migrar a esquema híbrido JWT o preparar para PQC JWT '
            'cuando se estandarice (IETF draft en progreso)'
        ),
    }
    return recommendations.get(
        algorithm,
        'Evaluar y migrar a alternativas post-cuánticas (FIPS 203/204/205)'
    )

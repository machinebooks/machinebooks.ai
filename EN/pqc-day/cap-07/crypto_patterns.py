"""
PQC-Day and the Machine — Chapter 7
Pattern: CRYPTO_PATTERNS dictionary for multi-language cryptographic detection

This is a didactic example from the book, not production code.
See chapter 7 for full context and explanation.
"""

# Cryptographic patterns organized by language.
# Each pattern includes: regex, severity, algorithm name,
# human-readable description, and PQC migration impact.

CRYPTO_PATTERNS = {
    'python': {
        'rsa_import': {
            'pattern': r'from\s+Crypto(?:dome)?\.PublicKey\s+import\s+RSA',
            'severity': 'critical',
            'algorithm': 'RSA',
            'description': 'RSA import (PyCryptodome)',
            'pqc_impact': 'RSA private key derivable with quantum computer'
        },
        'rsa_generate': {
            'pattern': r'RSA\.generate\s*\(\s*(\d+)',
            'severity': 'critical',
            'algorithm': 'RSA',
            'description': 'RSA key generation',
            'pqc_impact': 'Migrate to ML-KEM for key exchange'
        },
        'ecc_import': {
            'pattern': r'from\s+Crypto(?:dome)?\.PublicKey\s+import\s+ECC',
            'severity': 'critical',
            'algorithm': 'ECC',
            'description': 'Elliptic curve import (PyCryptodome)',
            'pqc_impact': 'ECC private key derivable with quantum computer'
        },
        'dh_cryptography': {
            'pattern': r'from\s+cryptography\.hazmat\.primitives\.asymmetric\s+import\s+dh',
            'severity': 'critical',
            'algorithm': 'DH',
            'description': 'Diffie-Hellman (cryptography library)',
            'pqc_impact': 'Key exchange vulnerable to Shor\'s algorithm'
        },
        'md5_hash': {
            'pattern': r'hashlib\.md5\s*\(|MD5\.new\s*\(',
            'severity': 'critical',
            'algorithm': 'MD5',
            'description': 'MD5 hash — broken even without quantum',
            'pqc_impact': 'MD5 has demonstrated collision attacks'
        },
        'sha1_hash': {
            'pattern': r'hashlib\.sha1\s*\(|SHA1?\.new\s*\(',
            'severity': 'high',
            'algorithm': 'SHA-1',
            'description': 'SHA-1 hash — deprecated',
            'pqc_impact': 'SHA-1 has demonstrated collisions (SHAttered)'
        },
        'des_import': {
            'pattern': r'from\s+Crypto(?:dome)?\.Cipher\s+import\s+DES',
            'severity': 'critical',
            'algorithm': 'DES',
            'description': 'DES cipher — broken',
            'pqc_impact': 'DES is broken without quantum computing'
        },
        'jwt_rs256': {
            'pattern': r'jwt\.(encode|decode)\s*\([^)]*algorithm\s*=\s*["\']RS(256|384|512)["\']',
            'severity': 'critical',
            'algorithm': 'RSA-JWT',
            'description': 'JWT signed with RSA',
            'pqc_impact': 'JWT signatures forgeable with quantum computer'
        },
        'jwt_es256': {
            'pattern': r'jwt\.(encode|decode)\s*\([^)]*algorithm\s*=\s*["\']ES(256|384|512)["\']',
            'severity': 'critical',
            'algorithm': 'ECDSA-JWT',
            'description': 'JWT signed with ECDSA',
            'pqc_impact': 'JWT signatures forgeable with quantum computer'
        },
    },

    'javascript': {
        'crypto_rsa': {
            'pattern': r'crypto\.generateKeyPair(?:Sync)?\s*\(\s*["\']rsa["\']',
            'severity': 'critical',
            'algorithm': 'RSA',
            'description': 'RSA key generation in Node.js',
            'pqc_impact': 'RSA is vulnerable to Shor\'s algorithm'
        },
        'crypto_dh': {
            'pattern': r'crypto\.createDiffieHellman\s*\(',
            'severity': 'critical',
            'algorithm': 'DH',
            'description': 'Diffie-Hellman in Node.js',
            'pqc_impact': 'DH is vulnerable to Shor\'s algorithm'
        },
        'webcrypto_rsa': {
            'pattern': r'subtle\.generateKey\s*\([^)]*RSASSA-PKCS1-v1_5|RSA-OAEP|RSA-PSS',
            'severity': 'critical',
            'algorithm': 'RSA',
            'description': 'WebCrypto API — RSA operations',
            'pqc_impact': 'RSA is vulnerable to Shor\'s algorithm'
        },
        'webcrypto_ecdsa': {
            'pattern': r'subtle\.generateKey\s*\([^)]*ECDSA',
            'severity': 'critical',
            'algorithm': 'ECDSA',
            'description': 'WebCrypto API — ECDSA operations',
            'pqc_impact': 'ECDSA is vulnerable to Shor\'s algorithm'
        },
    },

    # Java, Go, C/C++, Rust — analogous patterns
    # adapted to each ecosystem's APIs
}


# File extension to language mapping
LANGUAGE_EXTENSIONS = {
    'python': ['.py', '.pyw', '.pyi'],
    'javascript': ['.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'],
    'java': ['.java'],
    'go': ['.go'],
    'c': ['.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.hxx'],
    'rust': ['.rs'],
}

# Directories to exclude from scanning
SKIP_DIRECTORIES = {
    'node_modules', '.git', '.svn', '.hg',
    '__pycache__', '.pytest_cache',
    'venv', 'env', '.venv', '.env', 'virtualenv', '.tox',
    'build', 'dist', 'target', 'bin', 'obj', 'out',
    '.idea', '.vscode', '.vs',
    'vendor', 'third_party', 'external',
}


# PQC migration recommendations per algorithm
PQC_RECOMMENDATIONS = {
    'RSA': 'Migrate to ML-KEM (Kyber) for encryption or ML-DSA (Dilithium) for signatures',
    'DSA': 'Replace with ML-DSA (Dilithium) or SLH-DSA (SPHINCS+)',
    'ECDSA': 'Replace with ML-DSA (Dilithium) or SLH-DSA (SPHINCS+)',
    'ECC': 'Replace with ML-KEM (Kyber) for key exchange',
    'ECDH': 'Replace with ML-KEM (Kyber) for key encapsulation',
    'DH': 'Replace with ML-KEM (Kyber) for key encapsulation',
    'DES': 'Replace immediately with AES-256-GCM',
    '3DES': 'Replace with AES-256-GCM',
    'MD5': 'Replace with SHA-384 or SHA3-256 (post-quantum safe margin)',
    'SHA-1': 'Replace with SHA-384 or SHA3-256 (post-quantum safe margin)',
    'AES-128': 'Upgrade to AES-256 for post-quantum margin',
    'RSA-JWT': 'Prepare migration to hybrid JWT or PQC-JWT when standardized',
    'ECDSA-JWT': 'Prepare migration to hybrid JWT or PQC-JWT when standardized',
}


if __name__ == '__main__':
    # Print summary of all patterns
    total = 0
    for lang, patterns in CRYPTO_PATTERNS.items():
        print(f"\n{lang.upper()}: {len(patterns)} patterns")
        for name, info in patterns.items():
            print(f"  [{info['severity']:8s}] {info['algorithm']:10s} — {info['description']}")
            total += 1
    print(f"\nTotal patterns: {total}")
    print(f"Languages covered: {len(CRYPTO_PATTERNS)}")
    print(f"Supported extensions: {sum(len(v) for v in LANGUAGE_EXTENSIONS.values())}")

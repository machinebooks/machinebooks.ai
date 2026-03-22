# Extraído de: LibroPQC/cap-07-analisis-codigo.md
CRYPTO_PATTERNS = {
    'python': {
        'rsa_import': {
            'pattern': r'from\s+Crypto(?:dome)?\.PublicKey\s+import\s+RSA',
            'severity': 'critical',
            'algorithm': 'RSA',
            'description': 'Importación de RSA (PyCryptodome)',
            'pqc_impact': 'Clave privada RSA derivable con ordenador cuántico'
        },
        'rsa_generate': {
            'pattern': r'RSA\.generate\s*\(\s*(\d+)',
            'severity': 'critical',
            'algorithm': 'RSA',
            'description': 'Generación de clave RSA',
            'pqc_impact': 'Migrar a ML-KEM para intercambio de claves'
        },
        'ecc_import': {
            'pattern': r'from\s+Crypto(?:dome)?\.PublicKey\s+import\s+ECC',
            'severity': 'critical',
            'algorithm': 'ECC',
            'description': 'Importación de curvas elípticas (PyCryptodome)',
            'pqc_impact': 'Clave privada ECC derivable con ordenador cuántico'
        },
        'dh_cryptography': {
            'pattern': r'from\s+cryptography\.hazmat\.primitives\.asymmetric\s+import\s+dh',
            'severity': 'critical',
            'algorithm': 'DH',
            'description': 'Diffie-Hellman (biblioteca cryptography)',
            'pqc_impact': 'Intercambio de claves vulnerable a Shor'
        },
        'md5_hash': {
            'pattern': r'hashlib\.md5\s*\(|MD5\.new\s*\(',
            'severity': 'critical',
            'algorithm': 'MD5',
            'description': 'Hash MD5 — roto incluso sin cuántica',
            'pqc_impact': 'MD5 tiene ataques de colisión demostrados'
        },
        'sha1_hash': {
            'pattern': r'hashlib\.sha1\s*\(|SHA1?\.new\s*\(',
            'severity': 'high',
            'algorithm': 'SHA-1',
            'description': 'Hash SHA-1 — deprecado',
            'pqc_impact': 'SHA-1 tiene colisiones demostradas (SHAttered)'
        },
        'des_import': {
            'pattern': r'from\s+Crypto(?:dome)?\.Cipher\s+import\s+DES',
            'severity': 'critical',
            'algorithm': 'DES',
            'description': 'Cifrado DES — roto',
            'pqc_impact': 'DES está roto sin necesidad de cuántica'
        },
        'jwt_rs256': {
            'pattern': r'jwt\.(encode|decode)\s*\([^)]*algorithm\s*=\s*["\']RS(256|384|512)["\']',
            'severity': 'critical',
            'algorithm': 'RSA-JWT',
            'description': 'JWT firmado con RSA',
            'pqc_impact': 'Firmas JWT falsificables con ordenador cuántico'
        },
        'jwt_es256': {
            'pattern': r'jwt\.(encode|decode)\s*\([^)]*algorithm\s*=\s*["\']ES(256|384|512)["\']',
            'severity': 'critical',
            'algorithm': 'ECDSA-JWT',
            'description': 'JWT firmado con ECDSA',
            'pqc_impact': 'Firmas JWT falsificables con ordenador cuántico'
        },
    },

    'javascript': {
        'crypto_rsa': {
            'pattern': r'crypto\.generateKeyPair(?:Sync)?\s*\(\s*["\']rsa["\']',
            'severity': 'critical',
            'algorithm': 'RSA',
            'description': 'Generación de clave RSA en Node.js',
            'pqc_impact': 'RSA es vulnerable al algoritmo de Shor'
        },
        'crypto_dh': {
            'pattern': r'crypto\.createDiffieHellman\s*\(',
            'severity': 'critical',
            'algorithm': 'DH',
            'description': 'Diffie-Hellman en Node.js',
            'pqc_impact': 'DH es vulnerable al algoritmo de Shor'
        },
        'webcrypto_rsa': {
            'pattern': r'subtle\.generateKey\s*\([^)]*RSASSA-PKCS1-v1_5|RSA-OAEP|RSA-PSS',
            'severity': 'critical',
            'algorithm': 'RSA',
            'description': 'WebCrypto API — operaciones RSA',
            'pqc_impact': 'RSA es vulnerable al algoritmo de Shor'
        },
        'webcrypto_ecdsa': {
            'pattern': r'subtle\.generateKey\s*\([^)]*ECDSA',
            'severity': 'critical',
            'algorithm': 'ECDSA',
            'description': 'WebCrypto API — operaciones ECDSA',
            'pqc_impact': 'ECDSA es vulnerable al algoritmo de Shor'
        },
    },

    # Java, Go, C/C++, Rust — patrones análogos
    # adaptados a las APIs de cada ecosistema
}

# Extraído de: LibroPQC/cap-10-owasp.md
# Ejemplo didáctico: analyzers/owasp_analyzer.py — estructura de patrones

OWASP_PATTERNS = {
    'crypto_failures': {
        'hardcoded_secret': {
            # Regex que detecta asignaciones de secretos con valores literales
            'pattern': r'(?:secret|password|api_key|apikey|token|private_key)'
                       r'\s*[=:]\s*["\'][^"\']{8,}["\']',
            'severity': 'critical',
            'category': 'A02:2021',
            'title': 'Cryptographic Failures',
            'description': 'Secreto hardcodeado detectado en código fuente',
            'owasp_id': 'A02',
            'cwe': 'CWE-798',  # Uso de credenciales hardcodeadas
            'recommendation': 'Usar variables de entorno o gestor de secretos'
        },
        'weak_random': {
            # Detecta generadores pseudoaleatorios no criptográficos
            'pattern': r'(?:random\.random|Math\.random|'
                       r'rand\(\)|Random\(\)\.Next)',
            'severity': 'medium',
            'category': 'A02:2021',
            'title': 'Cryptographic Failures',
            'description': 'Generador pseudoaleatorio no criptográfico',
            'owasp_id': 'A02',
            'cwe': 'CWE-338',
            'recommendation': 'Usar secrets (Python) o crypto.randomBytes (Node.js)'
        },
    },
    'misconfiguration': {
        'ssl_verify_disabled': {
            # Detecta desactivación de verificación TLS en múltiples lenguajes
            'pattern': r'verify\s*[=:]\s*False|ssl\s*[=:]\s*False|'
                       r'VERIFY_NONE|rejectUnauthorized\s*:\s*false',
            'severity': 'critical',
            'category': 'A05:2021',
            'title': 'Security Misconfiguration',
            'description': 'Verificación SSL/TLS desactivada',
            'owasp_id': 'A05',
            'cwe': 'CWE-295',  # Validación impropia de certificados
            'recommendation': 'Verificar siempre los certificados SSL/TLS'
        },
        'cors_wildcard': {
            # Detecta CORS permisivo con wildcard
            'pattern': r'(?:Access-Control-Allow-Origin|cors|CORS)'
                       r'.*["\']?\*["\']?',
            'severity': 'medium',
            'category': 'A05:2021',
            'title': 'Security Misconfiguration',
            'description': 'CORS permite todos los orígenes (*)',
            'owasp_id': 'A05',
            'cwe': 'CWE-942',
            'recommendation': 'Restringir CORS a orígenes de confianza'
        },
    },
    'auth_failures': {
        'jwt_none_algorithm': {
            # Detecta JWT configurado con algoritmo none (bypass de firma)
            'pattern': r'(?:algorithm|alg)\s*[=:]\s*["\'](?:none|None)["\']',
            'severity': 'critical',
            'category': 'A07:2021',
            'title': 'Authentication Failures',
            'description': 'JWT con algoritmo none — bypass de autenticación',
            'owasp_id': 'A07',
            'cwe': 'CWE-327',  # Uso de algoritmo criptográfico roto o débil
            'recommendation': 'Siempre especificar y validar el algoritmo JWT'
        },
    },
    'injection': {
        'sql_injection': {
            # Detecta concatenación o interpolación en queries SQL
            'pattern': r'(?:execute|query|cursor\.execute|raw|rawQuery)\s*\('
                       r'\s*["\']?\s*(?:SELECT|INSERT|UPDATE|DELETE|DROP)'
                       r'[^"\']*%s|(?:f["\']|["\'].*\{).*'
                       r'(?:SELECT|INSERT|UPDATE|DELETE)',
            'severity': 'critical',
            'category': 'A03:2021',
            'title': 'Injection',
            'description': 'Potencial inyección SQL por interpolación de cadenas',
            'owasp_id': 'A03',
            'cwe': 'CWE-89',
            'recommendation': 'Usar consultas parametrizadas o un ORM'
        },
    },
    # ... 9 categorías adicionales con patrones similares
}

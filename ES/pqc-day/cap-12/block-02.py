# Extraído de: LibroPQC/cap-12-agente-autonomo.md
def _find_crypto_usage(self, crypto_type: str = "all") -> dict:
    """Busca uso de criptografía con patrones especializados."""
    crypto_patterns = {
        'rsa':   [r'RSA\s*[\(\.]', r'rsa[-_]?key', r'PKCS1', r'RSA_OAEP'],
        'aes':   [r'AES\s*[\(\.]', r'AES\.new', r'aes[-_]?encrypt'],
        'ecdsa': [r'ECDSA', r'ECC\s*[\(\.]', r'SigningKey', r'ec\.generate'],
        'ecdh':  [r'ECDH', r'X25519', r'X448', r'key[-_]?exchange'],
        'dh':    [r'DiffieHellman', r'DH\s*[\(\.]', r'dh[-_]?key'],
        'sha':   [r'SHA[-_]?1', r'SHA[-_]?256', r'hashlib\.sha'],
        'md5':   [r'MD5', r'hashlib\.md5'],
        'dsa':   [r'DSA\s*[\(\.]', r'dsa[-_]?key', r'DSA\.generate'],
    }

    # Construir patrón combinado según el tipo solicitado
    if crypto_type == 'all':
        patterns = [p for ps in crypto_patterns.values() for p in ps]
    else:
        patterns = crypto_patterns.get(crypto_type, [])

    combined = '|'.join(f'({p})' for p in patterns)

    # Ejecutar búsqueda y categorizar resultados
    raw = self._search_code(combined, None, is_regex=True, case_sensitive=False)

    if raw['success']:
        categorized = {}
        for match in raw['result']['matches']:
            for ctype, pats in crypto_patterns.items():
                if any(re.search(p, match['match'], re.I) for p in pats):
                    categorized.setdefault(ctype, []).append(match)
                    break

        return {
            'success': True,
            'result': {
                'categorized_matches': categorized,
                'summary': {k: len(v) for k, v in categorized.items()}
            }
        }
    return raw

# Extraído de: LibroBugBounty/cap-14-extension-tampering.md
import re
from pathlib import Path

def find_sha256_candidates(exe_path):
    """Busca candidatos a SHA-256 en un ejecutable."""
    data = Path(exe_path).read_bytes()

    # SHA-256 en minúsculas (lo más común en JavaScript/Node)
    pattern_lower = re.compile(rb'[0-9a-f]{64}')
    # SHA-256 en mayúsculas (menos común)
    pattern_upper = re.compile(rb'[0-9A-F]{64}')

    candidates = []
    for pattern in [pattern_lower, pattern_upper]:
        for match in pattern.finditer(data):
            # Verificar que no es parte de una string más larga
            start = match.start()
            end = match.end()
            before = data[start-1:start] if start > 0 else b'\x00'
            after = data[end:end+1] if end < len(data) else b'\x00'
            if before not in b'0123456789abcdefABCDEF' and \
               after not in b'0123456789abcdefABCDEF':
                candidates.append({
                    'offset': hex(start),
                    'hash': match.group().decode('ascii'),
                    'context': data[max(0,start-20):end+20]
                })

    return candidates

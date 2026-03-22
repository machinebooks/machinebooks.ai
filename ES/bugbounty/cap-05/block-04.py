# Extraído de: LibroBugBounty/cap-05-asar-tampering.md
# AnÃ¡lisis de strings del ejecutable de Wand IDE
# Claude identificÃ³ un patrÃ³n sospechoso

import pefile
from pathlib import Path

def find_hash_in_binary(exe_path: str) -> list[dict]:
    """Busca strings que parezcan hashes en el ejecutable."""
    data = Path(exe_path).read_bytes()
    results = []

    # Buscar patrones de hash: 64 caracteres hex (SHA-256)
    i = 0
    while i < len(data) - 64:
        # Verificar si hay 64 caracteres hexadecimales consecutivos
        candidate = data[i:i+64]
        try:
            text = candidate.decode('ascii')
            if all(c in '0123456789abcdef' for c in text):
                # Verificar contexto: bytes antes y despuÃ©s
                before = data[max(0,i-20):i]
                after = data[i+64:i+84]
                results.append({
                    "offset": hex(i),
                    "hash": text,
                    "context_before": before.hex(),
                    "context_after": after.hex(),
                })
            i += 64
        except (UnicodeDecodeError, ValueError):
            i += 1
            continue

    return results

# Resultado en Wand IDE:
# Offset 0x1A3F40: "a7b3c9d1e5f2...{64 chars}"
# Contexto: inmediatamente despuÃ©s de la string "integrity_hash"
# Esto es el SHA-256 esperado del app.asar

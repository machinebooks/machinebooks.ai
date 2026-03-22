# Extraído de: LibroBugBounty/cap-07-firma-codigo.md
# Script de detecciÃ³n de secrets hardcodeados en ASAR
# Claude generÃ³ este script tras encontrar patterns sospechosos

import re
from pathlib import Path

def scan_for_secrets(js_content: str) -> list[dict]:
    """Busca patrones de API keys y tokens en cÃ³digo JavaScript."""
    patterns = {
        "mixpanel": r'["\']([a-f0-9]{32})["\'].*[Mm]ixpanel',
        "launchdarkly": r'sdk-[a-zA-Z0-9\-]{20,}',
        "amplitude": r'["\']([a-f0-9]{32})["\'].*[Aa]mplitude',
        "generic_api_key": r'["\'](?:api[_-]?key|apikey|api_secret)["\']'
                           r'\s*[:=]\s*["\']([^"\']{16,})["\']',
        "jwt_token": r'eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}',
        "aws_access_key": r'AKIA[0-9A-Z]{16}',
        "private_key": r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----',
    }

    findings = []
    for name, pattern in patterns.items():
        matches = re.finditer(pattern, js_content)
        for match in matches:
            # Contexto: 50 caracteres antes y despuÃ©s
            start = max(0, match.start() - 50)
            end = min(len(js_content), match.end() + 50)
            context = js_content[start:end].replace('\n', ' ')

            findings.append({
                "type": name,
                "value_preview": match.group()[:20] + "...",
                "context": context,
                "severity": "HIGH" if name in (
                    "aws_access_key", "private_key", "jwt_token"
                ) else "MEDIUM",
            })

    return findings

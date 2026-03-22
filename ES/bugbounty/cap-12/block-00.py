# Extraído de: LibroBugBounty/cap-12-prompt-injection-rce.md
import re
import json
from pathlib import Path

def extract_system_prompts(extension_js_path):
    """Extrae system prompts de la extensión de Copilot Chat."""
    content = Path(extension_js_path).read_text(encoding='utf-8')

    # Patrones que contienen system prompts
    patterns = [
        r'system["\']:\s*["\'](.+?)["\']',    # system: "prompt..."
        r'systemMessage["\']:\s*["\'](.+?)["\']',
        r'instructions["\']:\s*["\'](.+?)["\']',
        r'You are .+?(?=["\']\s*[,}\]])',       # "You are..." prompts
    ]

    prompts = set()
    for pattern in patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        for match in matches:
            if len(match) > 50:  # Filtrar strings cortos
                prompts.add(match[:500])  # Truncar para legibilidad

    return sorted(prompts)

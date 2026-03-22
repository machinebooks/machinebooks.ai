# Extraído de: LibroBugBounty/cap-14-extension-tampering.md
import re
from pathlib import Path

def extract_hardcoded_secrets(js_path):
    """Extrae API keys hardcodeadas de un bundle JavaScript."""
    content = Path(js_path).read_text(encoding='utf-8', errors='ignore')

    patterns = {
        "Mixpanel": r'["\']([a-f0-9]{32})["\']',  # 32-char hex
        "LaunchDarkly": r'["\']sdk-[a-zA-Z0-9-]+["\']',
        "Amplitude": r'["\']([a-f0-9]{32})["\']',
        "GA_Measurement": r'["\']G-[A-Z0-9]+["\']',
        "Sentry_DSN": r'https://[a-f0-9]+@[a-z]+\.ingest\.sentry\.io/\d+',
    }

    findings = []
    for service, pattern in patterns.items():
        matches = re.findall(pattern, content)
        for match in matches:
            findings.append({"service": service, "key": match[:20] + "..."})

    return findings

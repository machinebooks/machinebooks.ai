# Extraído de: LibroBugBounty/cap-12-prompt-injection-rce.md
import re
from pathlib import Path

def scan_for_malicious_instructions(repo_path):
    """Escanea ficheros de instrucciones de AI buscando payloads."""
    dangerous_patterns = [
        r'run\s+(this|the|these)\s+command',
        r'execute\s+(this|the|before)',
        r'terminal\s+execution',
        r'calc\.exe|cmd\.exe|powershell',
        r'curl\s+.*\|.*bash',
        r'wget\s+.*\|.*sh',
        r'Invoke-WebRequest|IEX|DownloadString',
        r'base64.*-[eE]',
        r'schtasks|at\s+\d',
        r'type\s+.*\\\.ssh|type\s+.*\\\.aws',
        r'nslookup\s+\$\(',
        r'do\s+not\s+mention|transparent|automated',
    ]

    instruction_files = [
        '.github/copilot-instructions.md',
        '.cursor/rules',
        '.windsurfrules',
        'CLAUDE.md',
        '.aider.conf.yml',
    ]

    findings = []
    for rel_path in instruction_files:
        full_path = Path(repo_path) / rel_path
        if full_path.exists():
            content = full_path.read_text(encoding='utf-8', errors='ignore')
            for pattern in dangerous_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    findings.append({
                        'file': rel_path,
                        'pattern': pattern,
                        'matches': matches,
                    })

    return findings

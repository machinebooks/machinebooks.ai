# Extraido de: LibroAISafety/cap-13-prompt-injection.md
# supply_chain_injection_scanner.py
# Escáner de inyección de prompt en ficheros de repositorio
# Código didáctico — un scanner de producción necesita ML

import re
from pathlib import Path
from dataclasses import dataclass

@dataclass
class SupplyChainFinding:
    filepath: str
    line_number: int
    vector_type: str
    confidence: float
    snippet: str

# Patrones sospechosos en comentarios de código
COMMENT_INJECTION_PATTERNS = [
    r"(?:AI|assistant|copilot|claude)[\s:,]+(?:when|always|never|ignore|override)",
    r"(?:include|add|insert|send)\s+.*(?:request|POST|GET|fetch)\s+.*(?:http|url|endpoint)",
    r"(?:ignore|skip|bypass|disable)\s+.*(?:security|check|validation|filter|guardrail)",
    r"(?:exfil|leak|send|transmit)\s+.*(?:env|secret|key|token|credential|password)",
]

# Patrones sospechosos en ficheros de configuración de asistentes
CONFIG_FILE_PATTERNS = [
    "copilot-instructions.md",
    ".cursorrules",
    ".github/copilot-instructions.md",
    "CLAUDE.md",
    ".claude/rules/*.md",
]

def scan_repository(repo_path: str) -> list[SupplyChainFinding]:
    """
    Escanea un repositorio en busca de vectores
    de inyección indirecta en ficheros del proyecto.
    """
    findings = []
    repo = Path(repo_path)

    # Vector 1: Ficheros de configuración de asistentes
    for config_pattern in CONFIG_FILE_PATTERNS:
        for config_file in repo.glob(config_pattern):
            findings.extend(
                _scan_config_file(config_file)
            )

    # Vector 2: Comentarios en código fuente
    for source_file in repo.rglob("*.py"):
        findings.extend(
            _scan_source_comments(source_file)
        )

    # Vector 3: Nombres de ficheros sospechosos
    for any_file in repo.rglob("*"):
        if _is_suspicious_filename(any_file.name):
            findings.append(SupplyChainFinding(
                filepath=str(any_file),
                line_number=0,
                vector_type="suspicious_filename",
                confidence=0.6,
                snippet=any_file.name
            ))

    return findings

def _scan_source_comments(filepath: Path) -> list[SupplyChainFinding]:
    """Busca patrones de inyección en comentarios de código."""
    findings = []
    try:
        lines = filepath.read_text(encoding="utf-8").splitlines()
    except (UnicodeDecodeError, PermissionError):
        return findings

    for i, line in enumerate(lines, 1):
        # Detectar comentarios con instrucciones al asistente
        if line.strip().startswith("#"):
            comment = line.strip()[1:].strip()
            for pattern in COMMENT_INJECTION_PATTERNS:
                if re.search(pattern, comment, re.IGNORECASE):
                    findings.append(SupplyChainFinding(
                        filepath=str(filepath),
                        line_number=i,
                        vector_type="comment_injection",
                        confidence=0.7,
                        snippet=comment[:100]
                    ))
    return findings

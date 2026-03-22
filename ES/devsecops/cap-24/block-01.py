# Extraído de: LibroDevSecOps/cap-24-security-champions.md
from dataclasses import dataclass
from enum import Enum

class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"

@dataclass
class Finding:
    id: str
    title: str
    severity: Severity
    cwe: str
    file_path: str
    line: int
    code_snippet: str
    tool: str           # "semgrep", "grype", "trivy"
    suggested_fix: str

def generate_training_module(
    finding: Finding,
    team_stack: list[str]
) -> dict:
    """Genera módulo de microformación a partir de un hallazgo."""
    client = anthropic.Anthropic()

    prompt = f"""Genera un módulo de formación breve para un security champion
sobre el siguiente hallazgo de seguridad.

Hallazgo: {finding.title}
Severidad: {finding.severity.value}
CWE: {finding.cwe}
Herramienta: {finding.tool}
Archivo: {finding.file_path}:{finding.line}
Código afectado:

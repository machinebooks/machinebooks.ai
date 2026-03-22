# Extraído de: LibroDevSecOps/cap-08-orquestacion-pipeline.md
# scripts/security_aggregator.py
"""
Agregador de resultados de seguridad.
Lee los outputs JSON de SAST, SCA, secrets y container scan,
normaliza los hallazgos y aplica las reglas del gate.
"""
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class Finding:
    """Hallazgo normalizado de cualquier herramienta."""
    source: str          # sast | sca | secrets | container
    severity: str        # critical | high | medium | low | info
    title: str
    description: str
    location: str        # fichero:línea o paquete:versión
    cvss_score: float = 0.0
    cve_id: str = ""
    fixable: bool = False

@dataclass
class GateReport:
    """Resultado del gate de seguridad."""
    gate_decision: str = "pass"     # pass | warn | block
    block_reason: str = ""
    findings: list = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    pr_comment: str = ""


# ── Reglas del gate ────────────────────────────────
GATE_RULES = {
    "block": {
        "sast_critical": True,       # CWE inyección, deserialización
        "sca_critical_direct": True,  # CVSS >= 9.0 en dep directa
        "secrets_any": True,          # Cualquier secreto detectado
    },
    "warn": {
        "sca_high_direct": True,     # CVSS 7.0-8.9 en dep directa
        "sast_high": True,
        "container_critical_fixable": True,  # Crítica con parche
    },
}


def parse_semgrep(path: Path) -> list[Finding]:
    """Extrae hallazgos de la salida JSON de Semgrep."""
    data = json.loads(path.read_text())
    findings = []
    for result in data.get("results", []):
        severity_map = {
            "ERROR": "critical", "WARNING": "high",
            "INFO": "medium",
        }
        findings.append(Finding(
            source="sast",
            severity=severity_map.get(result["extra"]["severity"], "info"),
            title=result["check_id"],
            description=result["extra"].get("message", ""),
            location=f"{result['path']}:{result['start']['line']}",
        ))
    return findings


def parse_grype(path: Path) -> list[Finding]:
    """Extrae hallazgos de la salida JSON de Grype."""
    data = json.loads(path.read_text())
    findings = []
    for match in data.get("matches", []):
        vuln = match["vulnerability"]
        cvss = 0.0
        for score in vuln.get("cvss", []):
            if score.get("metrics", {}).get("baseScore", 0) > cvss:
                cvss = score["metrics"]["baseScore"]
        severity = vuln.get("severity", "Unknown").lower()
        pkg = match["artifact"]
        findings.append(Finding(
            source="sca",
            severity=severity,
            title=f"{pkg['name']}@{pkg['version']}",
            description=vuln.get("description", ""),
            location=f"{pkg['name']}:{pkg['version']}",
            cvss_score=cvss,
            cve_id=vuln.get("id", ""),
            fixable=bool(vuln.get("fix", {}).get("versions")),
        ))
    return findings


def parse_gitleaks(path: Path) -> list[Finding]:
    """Extrae hallazgos de la salida JSON de Gitleaks."""
    data = json.loads(path.read_text())
    findings = []
    for leak in data if isinstance(data, list) else []:
        findings.append(Finding(
            source="secrets",
            severity="critical",  # Todo secreto es crítico
            title=leak.get("RuleID", "unknown-secret"),
            description=leak.get("Description", "Secret detected"),
            location=f"{leak.get('File', '?')}:{leak.get('StartLine', '?')}",
        ))
    return findings


def parse_trivy(path: Path) -> list[Finding]:
    """Extrae hallazgos de la salida JSON de Trivy."""
    data = json.loads(path.read_text())
    findings = []
    for result in data.get("Results", []):
        for vuln in result.get("Vulnerabilities", []):
            findings.append(Finding(
                source="container",
                severity=vuln.get("Severity", "UNKNOWN").lower(),
                title=f"{vuln.get('PkgName', '?')}@"
                      f"{vuln.get('InstalledVersion', '?')}",
                description=vuln.get("Title", ""),
                location=f"{result.get('Target', '?')}",
                cvss_score=vuln.get(
                    "CVSS", {}
                ).get("nvd", {}).get("V3Score", 0.0),
                cve_id=vuln.get("VulnerabilityID", ""),
                fixable=bool(vuln.get("FixedVersion")),
            ))
    return findings

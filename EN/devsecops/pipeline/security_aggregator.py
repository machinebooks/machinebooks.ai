# Source: The DevSecOps and the Machine -- Chapter 8
# Pattern: Multi-tool security aggregator with gate logic

# scripts/security_aggregator.py
"""
Security results aggregator.
Reads JSON outputs from SAST, SCA, secrets, and container scan,
normalizes findings, and applies gate rules.
"""
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class Finding:
    """Normalized finding from any tool."""
    source: str          # sast | sca | secrets | container
    severity: str        # critical | high | medium | low | info
    title: str
    description: str
    location: str        # file:line or package:version
    cvss_score: float = 0.0
    cve_id: str = ""
    fixable: bool = False

@dataclass
class GateReport:
    """Security gate result."""
    gate_decision: str = "pass"     # pass | warn | block
    block_reason: str = ""
    findings: list = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    pr_comment: str = ""


# ── Gate rules ────────────────────────────────────
GATE_RULES = {
    "block": {
        "sast_critical": True,       # Injection CWE, deserialization
        "sca_critical_direct": True,  # CVSS >= 9.0 in direct dep
        "secrets_any": True,          # Any detected secret
    },
    "warn": {
        "sca_high_direct": True,     # CVSS 7.0-8.9 in direct dep
        "sast_high": True,
        "container_critical_fixable": True,  # Critical with patch
    },
}


def parse_semgrep(path: Path) -> list[Finding]:
    """Extracts findings from Semgrep JSON output."""
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
    """Extracts findings from Grype JSON output."""
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
    """Extracts findings from Gitleaks JSON output."""
    data = json.loads(path.read_text())
    findings = []
    for leak in data if isinstance(data, list) else []:
        findings.append(Finding(
            source="secrets",
            severity="critical",  # Every secret is critical
            title=leak.get("RuleID", "unknown-secret"),
            description=leak.get("Description", "Secret detected"),
            location=f"{leak.get('File', '?')}:{leak.get('StartLine', '?')}",
        ))
    return findings


def parse_trivy(path: Path) -> list[Finding]:
    """Extracts findings from Trivy JSON output."""
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

def apply_gate(findings: list[Finding]) -> GateReport:
    """Applies gate rules to normalized findings."""
    report = GateReport()
    report.findings = findings

    # Counters by source and severity
    counts = {}
    for f in findings:
        key = f"{f.source}_{f.severity}"
        counts[key] = counts.get(key, 0) + 1

    report.summary = {
        "total": len(findings),
        "by_severity": {},
        "by_source": {},
    }
    for f in findings:
        report.summary["by_severity"][f.severity] = (
            report.summary["by_severity"].get(f.severity, 0) + 1
        )
        report.summary["by_source"][f.source] = (
            report.summary["by_source"].get(f.source, 0) + 1
        )

    # ── Blocking rules ────────────────────────────
    block_reasons = []

    # Secrets: any finding blocks
    if counts.get("secrets_critical", 0) > 0:
        block_reasons.append(
            f"🔴 {counts['secrets_critical']} secret(s) detected"
        )

    # Critical SAST: blocks
    if counts.get("sast_critical", 0) > 0:
        block_reasons.append(
            f"🔴 {counts['sast_critical']} critical SAST finding(s)"
        )

    # Critical SCA in direct dependency
    sca_critical = [
        f for f in findings
        if f.source == "sca" and f.severity == "critical"
        and f.cvss_score >= 9.0
    ]
    if sca_critical:
        block_reasons.append(
            f"🔴 {len(sca_critical)} critical CVE(s) (CVSS >= 9.0)"
        )

    if block_reasons:
        report.gate_decision = "block"
        report.block_reason = "\n".join(block_reasons)
        return report

    # ── Warning rules ─────────────────────────────
    warn_reasons = []
    if counts.get("sca_high", 0) > 0:
        warn_reasons.append(
            f"⚠️ {counts['sca_high']} high CVE(s) in dependencies"
        )
    if counts.get("sast_high", 0) > 0:
        warn_reasons.append(
            f"⚠️ {counts['sast_high']} high SAST finding(s)"
        )

    container_crit_fixable = [
        f for f in findings
        if f.source == "container" and f.severity == "critical"
        and f.fixable
    ]
    if container_crit_fixable:
        warn_reasons.append(
            f"⚠️ {len(container_crit_fixable)} critical container "
            f"vulnerability(ies) with available patch"
        )

    if warn_reasons:
        report.gate_decision = "warn"

    return report


def generate_pr_comment(report: GateReport) -> str:
    """Generates the Markdown comment for the PR."""
    icons = {"pass": "✅", "warn": "⚠️", "block": "🚫"}
    labels = {
        "pass": "APPROVED",
        "warn": "REQUIRES REVIEW",
        "block": "BLOCKED",
    }

    icon = icons[report.gate_decision]
    label = labels[report.gate_decision]

    lines = [
        f"## {icon} Security Gate: {label}",
        "",
        f"**Total findings:** {report.summary['total']}",
        "",
        "| Severity | Count |",
        "|----------|-------|",
    ]
    for sev in ["critical", "high", "medium", "low", "info"]:
        count = report.summary["by_severity"].get(sev, 0)
        if count > 0:
            lines.append(f"| {sev.upper()} | {count} |")

    lines.extend(["", "| Source | Count |", "|--------|-------|"])
    source_labels = {
        "sast": "SAST (Semgrep)",
        "sca": "SCA (Grype)",
        "secrets": "Secrets (Gitleaks)",
        "container": "Container (Trivy)",
    }
    for src, label_src in source_labels.items():
        count = report.summary["by_source"].get(src, 0)
        if count > 0:
            lines.append(f"| {label_src} | {count} |")

    if report.gate_decision == "block":
        lines.extend([
            "", "### Reasons for blocking", "", report.block_reason,
        ])

    lines.extend([
        "",
        "---",
        "*Generated by the Security Pipeline "
        "— see artifacts for full detail.*",
    ])
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Security aggregator")
    parser.add_argument("--results-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    all_findings: list[Finding] = []

    # Parsers mapped to artifact paths
    parsers = {
        "sast-results/sast-results.json": parse_semgrep,
        "sca-results/sca-results.json": parse_grype,
        "secrets-results/secrets-results.json": parse_gitleaks,
        "container-results/container-results.json": parse_trivy,
    }

    for rel_path, parse_fn in parsers.items():
        full_path = results_dir / rel_path
        if full_path.exists():
            try:
                all_findings.extend(parse_fn(full_path))
                print(f"[OK] Parsed {rel_path}: "
                      f"{len(parse_fn(full_path))} findings")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"[ERROR] Failed to parse {rel_path}: {e}")
        else:
            print(f"[WARN] Missing results: {rel_path}")

    # Apply the gate
    report = apply_gate(all_findings)
    report.pr_comment = generate_pr_comment(report)

    # Serialize the report
    output_data = {
        "gate_decision": report.gate_decision,
        "block_reason": report.block_reason,
        "summary": report.summary,
        "pr_comment": report.pr_comment,
        "findings": [
            {
                "source": f.source,
                "severity": f.severity,
                "title": f.title,
                "location": f.location,
                "cve_id": f.cve_id,
                "fixable": f.fixable,
            }
            for f in report.findings
        ],
    }

    Path(args.output).write_text(json.dumps(output_data, indent=2))
    print(f"\nGate decision: {report.gate_decision.upper()}")
    print(f"Total findings: {report.summary['total']}")


if __name__ == "__main__":
    main()
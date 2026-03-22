# Extraído de: LibroDevSecOps/cap-08-orquestacion-pipeline.md
def apply_gate(findings: list[Finding]) -> GateReport:
    """Aplica las reglas del gate sobre los hallazgos normalizados."""
    report = GateReport()
    report.findings = findings

    # Contadores por fuente y severidad
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

    # ── Reglas bloqueantes ─────────────────────────
    block_reasons = []

    # Secretos: cualquier hallazgo bloquea
    if counts.get("secrets_critical", 0) > 0:
        block_reasons.append(
            f"🔴 {counts['secrets_critical']} secreto(s) detectado(s)"
        )

    # SAST crítico: bloquea
    if counts.get("sast_critical", 0) > 0:
        block_reasons.append(
            f"🔴 {counts['sast_critical']} hallazgo(s) SAST crítico(s)"
        )

    # SCA crítica en dependencia directa
    sca_critical = [
        f for f in findings
        if f.source == "sca" and f.severity == "critical"
        and f.cvss_score >= 9.0
    ]
    if sca_critical:
        block_reasons.append(
            f"🔴 {len(sca_critical)} CVE crítica(s) (CVSS >= 9.0)"
        )

    if block_reasons:
        report.gate_decision = "block"
        report.block_reason = "\n".join(block_reasons)
        return report

    # ── Reglas de advertencia ──────────────────────
    warn_reasons = []
    if counts.get("sca_high", 0) > 0:
        warn_reasons.append(
            f"⚠️ {counts['sca_high']} CVE alta(s) en dependencias"
        )
    if counts.get("sast_high", 0) > 0:
        warn_reasons.append(
            f"⚠️ {counts['sast_high']} hallazgo(s) SAST alto(s)"
        )

    container_crit_fixable = [
        f for f in findings
        if f.source == "container" and f.severity == "critical"
        and f.fixable
    ]
    if container_crit_fixable:
        warn_reasons.append(
            f"⚠️ {len(container_crit_fixable)} vulnerabilidad(es) crítica(s) "
            f"en imagen con parche disponible"
        )

    if warn_reasons:
        report.gate_decision = "warn"

    return report


def generate_pr_comment(report: GateReport) -> str:
    """Genera el comentario Markdown para la PR."""
    icons = {"pass": "✅", "warn": "⚠️", "block": "🚫"}
    labels = {
        "pass": "APROBADO",
        "warn": "REQUIERE REVISIÓN",
        "block": "BLOQUEADO",
    }

    icon = icons[report.gate_decision]
    label = labels[report.gate_decision]

    lines = [
        f"## {icon} Security Gate: {label}",
        "",
        f"**Hallazgos totales:** {report.summary['total']}",
        "",
        "| Severidad | Cantidad |",
        "|-----------|----------|",
    ]
    for sev in ["critical", "high", "medium", "low", "info"]:
        count = report.summary["by_severity"].get(sev, 0)
        if count > 0:
            lines.append(f"| {sev.upper()} | {count} |")

    lines.extend(["", "| Fuente | Cantidad |", "|--------|----------|"])
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
            "", "### Motivos del bloqueo", "", report.block_reason,
        ])

    lines.extend([
        "",
        "---",
        "*Generado por el Security Pipeline "
        "— véase artefactos para detalle completo.*",
    ])
    return "\n".join(lines)

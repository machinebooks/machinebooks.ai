# Extraído de: LibroDevSecOps/cap-12-dast-inteligente.md
def generate_consolidated_report(
    zap_analysis: dict,
    nuclei_findings: dict,
    logic_test_results: list[dict],
    scan_metadata: dict,
) -> dict:
    """Genera informe consolidado de DAST para tres audiencias."""
    all_findings = []

    # Consolidar hallazgos de ZAP (ya filtrados por Claude)
    for f in zap_analysis.get("findings", []):
        if f["classification"] in ("REAL", "PROBABLE"):
            all_findings.append({
                "source": "ZAP",
                "name": f["alert_name"],
                "severity": f.get("severity", "MEDIUM"),
                "classification": f["classification"],
                "confidence": f["confidence"],
                "reasoning": f["reasoning"],
                "action": f["recommended_action"],
                "cwe": f.get("cwe", ""),
            })

    # Consolidar hallazgos de Nuclei
    for f in nuclei_findings.get("findings", []):
        all_findings.append({
            "source": "Nuclei",
            "name": f.get("info", {}).get("name", "Unknown"),
            "severity": f.get("info", {}).get("severity", "medium").upper(),
            "classification": "REAL",
            "confidence": 0.9,
            "reasoning": f.get("info", {}).get("description", ""),
            "action": f.get("info", {}).get("remediation", "Revisar configuración"),
            "cwe": f.get("info", {}).get("classification", {}).get("cwe-id", [""])[0],
        })

    # Consolidar tests de lógica de negocio
    for t in logic_test_results:
        if t.get("vulnerable", False):
            all_findings.append({
                "source": "Logic Test",
                "name": t["test_name"],
                "severity": t.get("severity", "MEDIUM"),
                "classification": "PROBABLE",
                "confidence": 0.7,
                "reasoning": t.get("evidence", ""),
                "action": "Verificar manualmente el flujo de negocio",
                "cwe": t.get("cwe", "CWE-840"),
            })

    # Ordenar por severidad
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    all_findings.sort(key=lambda f: severity_order.get(f["severity"], 4))

    return {
        "metadata": scan_metadata,
        "findings": all_findings,
        "summary": {
            "total_findings": len(all_findings),
            "by_severity": {
                s: len([f for f in all_findings if f["severity"] == s])
                for s in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
            },
            "by_source": {
                s: len([f for f in all_findings if f["source"] == s])
                for s in ["ZAP", "Nuclei", "Logic Test"]
            },
            "by_classification": {
                c: len([f for f in all_findings if f["classification"] == c])
                for c in ["REAL", "PROBABLE"]
            },
        },
        # Vista ejecutiva para el security lead
        "executive_summary": generate_executive_summary(all_findings),
    }

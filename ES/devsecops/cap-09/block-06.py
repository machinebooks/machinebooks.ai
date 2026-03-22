# Extraído de: LibroDevSecOps/cap-09-agente-triaje.md
from claude_agent_sdk import tool

@tool
def correlate_findings(
    service_name: str,
    cve_id: str | None,
    cwe_id: str | None,
    current_findings: list[dict]
) -> dict:
    """Busca hallazgos relacionados: mismo servicio, misma CVE,
    mismo CWE o mismo patrón de vulnerabilidad."""
    correlations = {
        "same_service": [],
        "same_cve": [],
        "same_cwe_pattern": [],
        "recurrent": False,
        "cluster_size": 0,
    }

    for f in current_findings:
        # Hallazgos en el mismo servicio
        if f.get("service_name") == service_name:
            correlations["same_service"].append(f["id"])

        # Misma CVE en diferentes servicios
        if cve_id and f.get("cve_id") == cve_id:
            correlations["same_cve"].append(f["id"])

        # Mismo patrón CWE (misma clase de vulnerabilidad)
        if cwe_id and f.get("cwe_id") == cwe_id:
            correlations["same_cwe_pattern"].append(f["id"])

    correlations["cluster_size"] = len(
        set(correlations["same_service"]
            + correlations["same_cve"]
            + correlations["same_cwe_pattern"])
    )

    # Un cluster grande sugiere un problema sistémico
    if correlations["cluster_size"] > 5:
        correlations["systemic_issue"] = True
    else:
        correlations["systemic_issue"] = False

    return correlations

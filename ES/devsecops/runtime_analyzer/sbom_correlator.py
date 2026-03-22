# Extraído de: LibroDevSecOps/cap-18-runtime-security.md
# runtime_analyzer/sbom_correlator.py
"""
Correlaciona alertas de Falco con vulnerabilidades
conocidas del SBOM para enriquecer el contexto de análisis.
"""
import json
from pathlib import Path


def load_sbom(container_image: str) -> dict:
    """Carga el SBOM CycloneDX generado por Syft."""
    sbom_path = Path(f"sboms/{container_image}.cdx.json")
    if not sbom_path.exists():
        return {"components": [], "vulnerabilities": []}
    return json.loads(sbom_path.read_text())


def find_relevant_cves(
    sbom: dict,
    alert_type: str
) -> list[dict]:
    """
    Busca CVEs en el SBOM que sean relevantes para
    el tipo de alerta de Falco.

    Mapeo de tipos de alerta a categorías de CVE:
    - network → RCE, SSRF, information disclosure
    - filesystem → path traversal, arbitrary file write
    - process → command injection, privilege escalation
    """
    type_to_cwe = {
        "network": ["CWE-918", "CWE-200", "CWE-94"],
        "filesystem": ["CWE-22", "CWE-73"],
        "process": ["CWE-78", "CWE-269"]
    }

    relevant_cwes = type_to_cwe.get(alert_type, [])
    relevant_vulns = []

    for vuln in sbom.get("vulnerabilities", []):
        for cwe in vuln.get("cwes", []):
            if cwe.get("id") in relevant_cwes:
                relevant_vulns.append({
                    "id": vuln.get("id"),
                    "severity": vuln.get("severity"),
                    "component": vuln.get("affects", [{}])[0]
                        .get("ref", "unknown"),
                    "description": vuln.get("description", "")
                })

    return relevant_vulns


def enrich_alert_context(
    container_name: str,
    alert_tags: list[str]
) -> str:
    """Genera contexto adicional para el agente Claude."""
    # Determinar tipo de alerta desde los tags de Falco
    alert_type = "unknown"
    if "network" in alert_tags or "mitre_exfiltration" in alert_tags:
        alert_type = "network"
    elif "filesystem" in alert_tags or "mitre_persistence" in alert_tags:
        alert_type = "filesystem"
    elif "mitre_execution" in alert_tags:
        alert_type = "process"

    image = get_container_image(container_name)
    sbom = load_sbom(image)
    cves = find_relevant_cves(sbom, alert_type)

    if not cves:
        return "No se encontraron CVEs relevantes en el SBOM."

    context = "CVEs relevantes en el SBOM del contenedor:\n"
    for cve in cves[:5]:  # Limitar a las 5 más relevantes
        context += (f"- {cve['id']} ({cve['severity']}): "
                   f"{cve['component']} — {cve['description'][:100]}\n")

    return context

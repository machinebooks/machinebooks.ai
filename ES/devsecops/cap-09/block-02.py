# Extraído de: LibroDevSecOps/cap-09-agente-triaje.md
import httpx
from claude_agent_sdk import tool

@tool
def query_cve_database(cve_id: str) -> dict:
    """Consulta NVD y OSV para obtener información detallada
    de una CVE: vector de ataque, exploit público, parche."""
    result = {
        "cve_id": cve_id,
        "attack_vector": None,
        "exploit_public": False,
        "patch_available": False,
        "references": [],
        "epss_score": None,  # Probabilidad de explotación
    }

    # Consulta NVD (National Vulnerability Database)
    nvd_url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}"
    resp = httpx.get(nvd_url, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        vulns = data.get("vulnerabilities", [])
        if vulns:
            cve_data = vulns[0]["cve"]
            metrics = cve_data.get("metrics", {})
            # Extraer vector de ataque de CVSS v3.1
            cvss_v31 = metrics.get("cvssMetricV31", [])
            if cvss_v31:
                vector = cvss_v31[0]["cvssData"]["attackVector"]
                result["attack_vector"] = vector

            # Verificar si hay referencias a exploits
            refs = cve_data.get("references", [])
            for ref in refs:
                tags = ref.get("tags", [])
                if "Exploit" in tags:
                    result["exploit_public"] = True
                if "Patch" in tags:
                    result["patch_available"] = True
                result["references"].append(ref["url"])

    # Consulta EPSS (Exploit Prediction Scoring System)
    epss_url = f"https://api.first.org/data/v1/epss?cve={cve_id}"
    resp_epss = httpx.get(epss_url, timeout=10)
    if resp_epss.status_code == 200:
        epss_data = resp_epss.json().get("data", [])
        if epss_data:
            result["epss_score"] = float(epss_data[0]["epss"])

    return result

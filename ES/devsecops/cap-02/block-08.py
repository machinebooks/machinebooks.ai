# Extraído de: LibroDevSecOps/cap-02-anatomia-vulnerabilidad.md
from claude_agent_sdk import Agent, tool

@tool
def get_service_context(service_name: str) -> dict:
    """Consulta el inventario de servicios y devuelve el contexto de seguridad."""
    import yaml
    with open("services_inventory.yaml") as f:
        inventory = yaml.safe_load(f)
    return inventory["services"].get(service_name, {"error": "Servicio no encontrado"})

@tool
def get_cve_details(cve_id: str) -> dict:
    """Consulta la base de datos NVD para obtener detalles de una CVE."""
    import requests
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        return response.json()
    return {"error": f"CVE {cve_id} no encontrada"}

@tool
def check_exploitability(cwe_id: str) -> dict:
    """Verifica si existen exploits públicos para el tipo de debilidad dado."""
    # Consulta simplificada a la base de datos de exploits
    known_exploitable = {
        "CWE-89": {"exploitable": True, "exploit_count": 1247, "ease": "trivial"},
        "CWE-79": {"exploitable": True, "exploit_count": 892, "ease": "easy"},
        "CWE-798": {"exploitable": True, "exploit_count": 156, "ease": "trivial"},
        "CWE-502": {"exploitable": True, "exploit_count": 203, "ease": "moderate"},
    }
    return known_exploitable.get(cwe_id, {"exploitable": False, "exploit_count": 0})

# Definición del agente de triaje
triage_agent = Agent(
    model="claude-sonnet-4-6",
    tools=[get_service_context, get_cve_details, check_exploitability],
    system_prompt="""Eres un analista de seguridad senior especializado en triaje
    de vulnerabilidades. Recibes hallazgos de herramientas SAST/SCA y los clasificas
    por riesgo real de negocio, no solo por severidad técnica.

    Para cada hallazgo:
    1. Consulta el contexto del servicio afectado
    2. Si hay una CVE asociada, consulta los detalles en NVD
    3. Verifica la explotabilidad del tipo de debilidad (CWE)
    4. Clasifica el riesgo real como CRITICAL, HIGH, MEDIUM, LOW o FALSE_POSITIVE
    5. Explica tu razonamiento en 2-3 frases
    6. Propón un fix concreto si el riesgo es MEDIUM o superior"""
)

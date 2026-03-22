# Extraído de: LibroDevSecOps/cap-05-sca-sbom.md
# scripts/triage_sca.py
"""
Triaje inteligente de hallazgos SCA.
Recibe resultados de Grype + SBOM y prioriza con Claude.
"""
import json
import sys
import anthropic

def load_results(grype_path: str, sbom_path: str) -> tuple:
    """Carga resultados de Grype y SBOM."""
    with open(grype_path) as f:
        vulnerabilities = json.load(f)
    with open(sbom_path) as f:
        sbom = json.load(f)
    return vulnerabilities, sbom

def build_context(vuln: dict, sbom: dict) -> str:
    """Construye el contexto para el análisis del agente."""
    artifact = vuln["artifact"]
    cve = vuln["vulnerability"]

    # Buscar dependencias inversas en el SBOM
    dependents = find_dependents(artifact["name"], sbom)

    return f"""
## Vulnerabilidad detectada

- **CVE**: {cve["id"]}
- **Severidad CVSS**: {cve["severity"]} ({cve["cvss"][0]["metrics"]["baseScore"]})
- **Paquete**: {artifact["name"]} v{artifact["version"]}
- **Ecosistema**: {artifact["type"]}
- **Descripción**: {cve["description"]}
- **Fix disponible**: {cve["fix"]["state"]} {cve["fix"].get("versions", [])}
- **Declarado en**: {artifact["locations"][0]["path"]}
- **Paquetes que dependen de este**: {', '.join(dependents) or 'ninguno (dependencia directa)'}

## Pregunta
Analiza esta vulnerabilidad en contexto. Considera:
1. ¿La función afectada es utilizada por la aplicación o es código muerto?
2. ¿El input que explota la CVE proviene de una fuente externa no confiable?
3. ¿Existe fix disponible y cuál es el riesgo de actualizar?
4. Prioridad recomendada: CRITICAL / HIGH / MEDIUM / LOW / ACCEPT
5. Acción recomendada: actualizar / mitigar / aceptar riesgo / investigar
"""

def find_dependents(package_name: str, sbom: dict) -> list:
    """Busca qué componentes dependen del paquete dado."""
    dependents = []
    for dep in sbom.get("dependencies", []):
        if any(package_name in d for d in dep.get("dependsOn", [])):
            dependents.append(dep.get("ref", "desconocido"))
    return dependents[:5]  # Limitar a 5 para no saturar el prompt

def triage_vulnerability(client, vuln: dict, sbom: dict) -> dict:
    """Triaja una vulnerabilidad individual con Claude."""
    context = build_context(vuln, sbom)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system="""Eres un analista de seguridad especializado en SCA.
Tu trabajo es priorizar vulnerabilidades en dependencias de terceros
considerando explotabilidad real, no solo CVSS teórico.
Responde en JSON con los campos: priority, action, reasoning, effort.
Sé conciso y preciso. No inventes datos que no estén en el contexto.""",
        messages=[{"role": "user", "content": context}]
    )

    return json.loads(message.content[0].text)

def main():
    grype_path = sys.argv[1]
    sbom_path = sys.argv[2]

    client = anthropic.Anthropic()  # Lee ANTHROPIC_API_KEY del entorno
    vulnerabilities, sbom = load_results(grype_path, sbom_path)

    results = []
    for match in vulnerabilities.get("matches", []):
        triage = triage_vulnerability(client, match, sbom)
        results.append({
            "cve": match["vulnerability"]["id"],
            "package": match["artifact"]["name"],
            "cvss": match["vulnerability"]["severity"],
            "triage": triage
        })

    # Ordenar por prioridad del agente, no por CVSS
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "ACCEPT": 4}
    results.sort(key=lambda r: priority_order.get(r["triage"]["priority"], 5))

    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

# Extraído de: LibroDevSecOps/cap-05-sca-sbom.md
# scripts/sbom_risk_report.py
"""
Agente que analiza un SBOM completo y genera un informe de riesgo.
Usa Claude para análisis holístico de la composición del proyecto.
"""
import json
import sys
import anthropic

def summarize_sbom(sbom: dict) -> dict:
    """Extrae métricas clave del SBOM para el análisis."""
    components = sbom.get("components", [])
    licenses = {}
    ecosystems = {}

    for comp in components:
        # Contar licencias
        for lic in comp.get("licenses", []):
            lic_id = lic.get("license", {}).get("id", "desconocida")
            licenses[lic_id] = licenses.get(lic_id, 0) + 1

        # Contar ecosistemas
        comp_type = comp.get("type", "desconocido")
        ecosystems[comp_type] = ecosystems.get(comp_type, 0) + 1

    return {
        "total_components": len(components),
        "license_distribution": licenses,
        "ecosystem_distribution": ecosystems,
        "components_without_license": sum(
            1 for c in components if not c.get("licenses")
        ),
    }

def generate_risk_report(
    sbom_path: str, grype_path: str
) -> str:
    """Genera el informe completo de riesgo de composición."""
    with open(sbom_path) as f:
        sbom = json.load(f)
    with open(grype_path) as f:
        vulns = json.load(f)

    summary = summarize_sbom(sbom)
    vuln_count = len(vulns.get("matches", []))
    critical = sum(
        1 for m in vulns["matches"]
        if m["vulnerability"]["severity"] == "Critical"
    )
    high = sum(
        1 for m in vulns["matches"]
        if m["vulnerability"]["severity"] == "High"
    )

    client = anthropic.Anthropic()

    prompt = f"""
## Datos del SBOM

- Total de componentes: {summary["total_components"]}
- Distribución de licencias: {json.dumps(summary["license_distribution"])}
- Componentes sin licencia declarada: {summary["components_without_license"]}
- Distribución por ecosistema: {json.dumps(summary["ecosystem_distribution"])}

## Datos de vulnerabilidades (Grype)

- Total de vulnerabilidades: {vuln_count}
- Critical: {critical}
- High: {high}

## Vulnerabilidades detalladas (top 10 por severidad)

{format_top_vulns(vulns, limit=10)}

## Solicitud

Genera un informe ejecutivo de riesgo de composición que incluya:
1. **Resumen ejecutivo** (3-5 líneas para el CISO)
2. **Riesgo de vulnerabilidades**: hallazgos prioritarios con recomendación
3. **Riesgo de licencias**: licencias copyleft o incompatibles detectadas
4. **Riesgo de supply chain**: dependencias sin mantenimiento o sin licencia
5. **Acciones recomendadas**: ordenadas por impacto y urgencia
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system="""Eres un analista de seguridad que genera informes de riesgo
de composición de software. Tu audiencia es el security lead y el CISO.
Sé conciso, cuantitativo y accionable. No incluyas recomendaciones
genéricas. Cada recomendación debe referirse a un hallazgo concreto
del SBOM o de las vulnerabilidades proporcionadas.""",
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text

def format_top_vulns(vulns: dict, limit: int = 10) -> str:
    """Formatea las N vulnerabilidades más severas para el prompt."""
    sorted_matches = sorted(
        vulns.get("matches", []),
        key=lambda m: m["vulnerability"]["cvss"][0]["metrics"]["baseScore"],
        reverse=True
    )[:limit]

    lines = []
    for m in sorted_matches:
        v = m["vulnerability"]
        a = m["artifact"]
        lines.append(
            f"- {v['id']} ({v['severity']}, CVSS {v['cvss'][0]['metrics']['baseScore']})"
            f" en {a['name']} v{a['version']}: {v['description'][:100]}"
        )
    return "\n".join(lines)

if __name__ == "__main__":
    report = generate_risk_report(sys.argv[1], sys.argv[2])
    print(report)

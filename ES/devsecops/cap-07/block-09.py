# Extraído de: LibroDevSecOps/cap-07-contenedores.md
import anthropic
import json
from pathlib import Path

def load_trivy_results(path: str) -> dict:
    """Carga resultados de Trivy desde fichero JSON."""
    return json.loads(Path(path).read_text())

def build_analysis_prompt(results: dict, context: dict) -> str:
    """Construye el prompt con resultados y contexto del servicio."""
    vulns = []
    for result in results.get("Results", []):
        for vuln in result.get("Vulnerabilities", []):
            vulns.append({
                "id": vuln["VulnerabilityID"],
                "severity": vuln["Severity"],
                "pkg": vuln["PkgName"],
                "installed": vuln["InstalledVersion"],
                "fixed": vuln.get("FixedVersion", "sin fix disponible"),
                "title": vuln.get("Title", ""),
            })

    return f"""Analiza estos hallazgos de Trivy sobre la imagen
del servicio {context['service_name']}.

Contexto del servicio:
- Expuesto a internet: {context['internet_facing']}
- Datos sensibles: {context['handles_sensitive_data']}
- Imagen base actual: {context['base_image']}

Hallazgos ({len(vulns)} vulnerabilidades):
{json.dumps(vulns, indent=2)}

Genera un informe con:
1. Hallazgos que requieren acción inmediata (con justificación)
2. Para cada hallazgo crítico: pasos concretos de remediación
3. Hallazgos que pueden aceptarse temporalmente (con justificación)
4. Si procede: recomendación de cambio de imagen base
5. Cambios específicos al Dockerfile para reducir superficie"""

def analyze_trivy_results():
    """Ejecuta el análisis de resultados de Trivy con Claude."""
    client = anthropic.Anthropic()

    # Carga resultados de los tres modos de escaneo
    image_results = load_trivy_results("trivy-image.json")
    config_results = load_trivy_results("trivy-config.json")

    # Contexto del servicio (configurable por repositorio)
    context = {
        "service_name": "api-gateway",
        "internet_facing": True,
        "handles_sensitive_data": True,
        "base_image": "python:3.12-slim-bookworm",
    }

    prompt = build_analysis_prompt(image_results, context)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": prompt,
        }],
        system="""Eres un especialista en seguridad de contenedores.
Prioriza por explotabilidad real, no solo por CVSS.
Un CVE crítico en un paquete que la aplicación no usa
tiene menor prioridad que un CVE alto en una biblioteca
que procesa input del usuario. Sé conciso y accionable.""",
    )

    report = message.content[0].text
    Path("trivy-analysis.md").write_text(report)
    print(report)

if __name__ == "__main__":
    analyze_trivy_results()

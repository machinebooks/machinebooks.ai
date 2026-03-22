# Extraído de: LibroPQC/cap-25-mercado.md
import anthropic


def generate_sector_analysis(
    org_metrics: dict,
    sector_averages: dict,
    framework_id: str,
) -> str:
    """Genera análisis comparativo de posición PQC
    de la organización frente a su sector usando Claude."""

    client = anthropic.Anthropic()

    # Construir prompt con datos estructurados
    prompt = f"""Analiza la posición de preparación post-cuántica de esta
organización frente a las medias de su sector. Genera un informe ejecutivo
en español con recomendaciones priorizadas.

## Métricas de la organización
- Algoritmos quantum-vulnerables detectados: {org_metrics['vuln_count']}
- Porcentaje PQC-compliant: {org_metrics['pqc_pct']}%
- Certificados con RSA/ECDSA: {org_metrics['legacy_certs']}
- Dependencias con crypto vulnerable: {org_metrics['vuln_deps']}
- Días hasta deadline {framework_id}: {org_metrics['days_to_deadline']}

## Medias del sector ({org_metrics['sector']})
- Algoritmos vulnerables (media): {sector_averages['avg_vuln']}
- PQC-compliant (media): {sector_averages['avg_pqc_pct']}%
- Certificados legacy (media): {sector_averages['avg_legacy_certs']}

## Instrucciones
1. Comparar posición relativa (por encima/debajo de la media)
2. Identificar las 3 áreas de mayor riesgo
3. Proponer acciones priorizadas por urgencia regulatoria
4. Incluir estimación de esfuerzo (meses/equipo)
5. NO inventar datos — usar solo los proporcionados
6. Mencionar regulaciones aplicables al sector"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text

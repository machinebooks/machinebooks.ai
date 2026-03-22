# Extraído de: LibroConsultor/cap-13-gap-analysis.md
def generate_executive_summary(
    gaps: list[GapFinding],
    roadmap: list[RemediationAction],
    org_profile: str,
) -> str:
    """Genera resumen ejecutivo con Claude Opus."""
    client = anthropic.Anthropic()

    # Preparar datos para la síntesis
    gap_summary = _format_gap_summary(gaps)
    roadmap_summary = _format_roadmap_summary(roadmap)

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        system="""Eres un consultor senior de seguridad y
compliance con 20 años de experiencia. Redacta un resumen
ejecutivo para la dirección de la organización. Tono: directo,
sin alarmismo pero sin minimizar. Incluye: posición actual,
riesgos principales, inversión estimada, plazo y beneficio
esperado. Máximo 2 páginas.""",
        messages=[{"role": "user", "content": f"""
Perfil de organización: {org_profile}

RESUMEN DE GAPS IDENTIFICADOS:
{gap_summary}

ROADMAP DE REMEDIACIÓN PROPUESTO:
{roadmap_summary}

Genera un resumen ejecutivo que incluya:
1. Posición global de cumplimiento (% por framework)
2. Los 5 riesgos más relevantes y su impacto potencial
3. Inversión total estimada (días-persona y plazo)
4. Recomendación estratégica: por dónde empezar y por qué
5. Qué pasa si no se actúa (coste de la inacción)"""}],
    )
    return response.content[0].text

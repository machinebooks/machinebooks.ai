# Extraído de: LibroCISO/cap-25-vigilancia-normativa.md
import anthropic

async def analyze_regulatory_impact(
    update_title: str,
    update_summary: str,
    active_frameworks: list[str],
    organization_sector: str,
) -> dict:
    """Analiza el impacto de una actualización normativa
    sobre los marcos y controles de la organización.

    Retorna: ai_summary, ai_impact_analysis,
             affected_frameworks, affected_controls
    """
    client = anthropic.Anthropic()

    prompt = f"""Eres un analista de cumplimiento normativo especializado
en regulación europea (RGPD, NIS2, DORA, ENS, AI Act, ISO 27001).

La organización opera en el sector: {organization_sector}
Marcos activos: {', '.join(active_frameworks)}

Se ha detectado esta actualización normativa:
- Título: {update_title}
- Resumen: {update_summary}

Analiza:
1. Resumen ejecutivo del cambio (3-5 líneas)
2. Marcos afectados de la lista activa
3. Controles específicos que pueden necesitar revisión
4. Severidad del impacto: info/warning/critical
5. Plazo estimado de adaptación

Responde en JSON con esta estructura:
{{
    "summary": "...",
    "impact_analysis": "...",
    "affected_frameworks": ["NIS2", "ENS"],
    "affected_controls": [
        {{"framework": "NIS2", "control_id": "21.2",
          "impact": "high", "reason": "..."}}
    ],
    "severity": "warning",
    "adaptation_deadline_days": 90
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    # Parsear respuesta JSON del LLM
    return parse_llm_response(message.content[0].text)

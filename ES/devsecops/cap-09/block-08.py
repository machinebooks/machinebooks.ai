# Extraído de: LibroDevSecOps/cap-09-agente-triaje.md
import anthropic
from claude_agent_sdk import Agent, tool
from dataclasses import asdict

# Inicializar cliente Anthropic
client = anthropic.Anthropic()

TRIAGE_SYSTEM_PROMPT = """Eres un agente de triaje de seguridad.
Tu función es analizar hallazgos de escaneo (SAST, SCA, contenedores)
y generar un plan de acción priorizado.

Para cada hallazgo:
1. Usa query_cve_database si tiene CVE para verificar explotabilidad.
2. Usa check_service_exposure para determinar la exposición del servicio.
3. Usa get_business_context para evaluar impacto de negocio.
4. Usa estimate_fix_complexity para estimar esfuerzo de corrección.
5. Usa correlate_findings para detectar patrones y clusters.

Criterios de priorización (pesos):
- Explotabilidad: 35% (exploit público, EPSS, vector de ataque)
- Exposición: 25% (internet-facing, autenticación, WAF)
- Impacto de negocio: 25% (datos sensibles, criticidad, compliance)
- Esfuerzo de corrección: 15% (inversamente — lo fácil primero a igualdad)

Genera puntuación 0-100 por hallazgo.
> 70: acción inmediata. 40-70: acción planificada. < 40: backlog.

Responde SIEMPRE con JSON estructurado."""

def run_triage_agent(findings: list[dict]) -> dict:
    """Ejecuta el agente de triaje sobre una lista de hallazgos
    normalizados y devuelve el plan de acción priorizado."""

    # Construir el mensaje con los hallazgos
    findings_text = "\n".join(
        f"- [{f['id']}] {f['source']}: {f['title']} "
        f"(severity={f['severity']}, service={f.get('service_name', 'unknown')})"
        for f in findings
    )

    agent = Agent(
        model="claude-haiku-4-5",  # Coste-eficiente para triaje
        system=TRIAGE_SYSTEM_PROMPT,
        tools=[
            query_cve_database,
            check_service_exposure,
            estimate_fix_complexity,
            correlate_findings,
            get_business_context,
        ],
        max_tool_calls=50,  # Límite para controlar coste
    )

    response = agent.run(
        messages=[{
            "role": "user",
            "content": f"""Analiza y prioriza estos {len(findings)}
hallazgos de seguridad:

{findings_text}

Genera el plan de acción priorizado con formato JSON:
{{
  "total_findings": N,
  "immediate_action": [...],
  "planned_action": [...],
  "backlog": [...],
  "systemic_issues": [...],
  "summary": "..."
}}"""
        }]
    )

    return response

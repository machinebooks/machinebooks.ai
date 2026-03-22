# Extraído de: LibroFinOps/cap-14-rightsizing-ia.md
# rightsizing_agent/agent.py
import anthropic
import json

client = anthropic.Anthropic()

RIGHTSIZING_SYSTEM_PROMPT = """Eres un experto en FinOps cloud especializado en rightsizing
de instancias. Tu función es analizar recomendaciones técnicas de AWS Compute Optimizer
y enriquecerlas con contexto de negocio para producir recomendaciones que un equipo
de ingeniería pueda aprobar con confianza.

Para cada candidato de rightsizing, debes:
1. Evaluar el riesgo real del cambio (no solo el técnico: considera el contexto del servicio)
2. Verificar si el timing propuesto es adecuado (¿hay despliegues planificados cerca?)
3. Estimar el ahorro con precisión (por mes y anualizado)
4. Recomendar el timing óptimo para el cambio
5. Identificar al propietario/equipo responsable que debe aprobar

IMPORTANTE:
- Sé directo: "Recomendamos cambiar a X porque Y. Riesgo: Z."
- El ahorro siempre en dólares, no en porcentaje
- Si el riesgo es alto o hay información insuficiente, recomienda "no actuar ahora"
- Distingue entre recomendaciones para entornos de producción vs dev/staging

Responde con un array JSON donde cada elemento tiene:
{
  "instance_id": "...",
  "current_type": "...",
  "recommended_type": "...",
  "monthly_savings_usd": ...,
  "annual_savings_usd": ...,
  "risk_level": "low|medium|high",
  "risk_explanation": "...",
  "recommendation": "Texto de 2-3 frases para el aprobador",
  "optimal_timing": "Cuándo hacer el cambio",
  "owner_team": "Equipo propietario si está en los tags"
}"""


async def generate_rightsizing_recommendations(
    business_context: str
) -> list[dict]:
    """
    Genera recomendaciones de rightsizing enriquecidas con contexto.
    Combina datos técnicos de AWS con razonamiento de Claude.
    """
    # Paso 1: obtenemos los candidatos de Compute Optimizer
    candidates = get_ec2_rightsizing_candidates()

    if not candidates['candidates']:
        return []

    # Paso 2: enriquecemos con métricas detalladas para los top candidatos
    # (limitamos a los 10 con mayor ahorro para controlar el coste de tokens)
    top_candidates = sorted(
        candidates['candidates'],
        key=lambda x: x['monthly_savings_usd'],
        reverse=True
    )[:10]

    enriched = []
    for candidate in top_candidates:
        detail = get_instance_utilization_detail(candidate['instance_id'])
        enriched.append({**candidate, 'detail': detail})

    # Paso 3: Claude analiza y enriquece con contexto de negocio
    user_message = f"""Analiza estos candidatos de rightsizing EC2:

{json.dumps(enriched, indent=2, default=str)}

Contexto de negocio actual:
{business_context}

Genera recomendaciones accionables para el workflow de aprobación.
Prioriza por ahorro anual descendente."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=RIGHTSIZING_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    try:
        return json.loads(response.content[0].text)
    except json.JSONDecodeError:
        return []

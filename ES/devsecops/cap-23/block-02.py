# Extraído de: LibroDevSecOps/cap-23-excepciones-deuda.md
import anthropic
import json
from datetime import datetime

client = anthropic.Anthropic()

RISK_ASSESSMENT_PROMPT = """Eres un analista de seguridad sénior que evalúa solicitudes
de excepción de seguridad en un pipeline DevSecOps.

Analiza la siguiente solicitud y genera un informe estructurado.

## Hallazgo
- ID: {finding_id}
- Fuente: {finding_source}
- Severidad: {severity}
- CVE: {cve_id}
- Componente afectado: {affected_component}
- Servicio: {service_name}

## Contexto del servicio
{service_context}

## Justificación del solicitante
- Negocio: {business_justification}
- Técnica: {technical_justification}

## Instrucciones de análisis
1. Evalúa la explotabilidad real considerando los controles existentes.
2. Asigna un risk_score de 0 (sin riesgo) a 100 (explotación inminente).
3. Sugiere entre 1 y 3 controles compensatorios específicos y viables.
4. Recomienda: aprobar, aprobar con controles, o denegar.
5. Si recomiendas aprobar, sugiere un plazo máximo de excepción en días.

Responde en JSON con esta estructura:
{{
  "risk_score": <int>,
  "exploitability_analysis": "<texto>",
  "compensating_controls": ["<control1>", "<control2>"],
  "recommendation": "approve|approve_with_controls|deny",
  "suggested_expiry_days": <int>,
  "reasoning": "<texto>"
}}"""


def assess_exception_risk(
    exception_data: dict,
    service_context: str
) -> dict:
    """Evalúa el riesgo de una solicitud de excepción con Claude."""

    prompt = RISK_ASSESSMENT_PROMPT.format(
        **exception_data,
        service_context=service_context
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )

    # Extraer JSON de la respuesta
    response_text = message.content[0].text
    assessment = json.loads(response_text)

    return {
        "risk_score": assessment["risk_score"],
        "exploitability_analysis": assessment["exploitability_analysis"],
        "compensating_controls": assessment["compensating_controls"],
        "recommendation": assessment["recommendation"],
        "suggested_expiry_days": assessment["suggested_expiry_days"],
        "reasoning": assessment["reasoning"],
        "tokens_used": message.usage.input_tokens + message.usage.output_tokens
    }

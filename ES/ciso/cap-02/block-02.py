# Extraído de: LibroCISO/cap-02-arquitecto-ia-regulatorio.md
# Ejemplo didáctico: patrones/agentes/privacy_risk_agent.py
# Agente que analiza un tratamiento y sugiere riesgos para DPIA

import anthropic

client = anthropic.Anthropic()

def analyze_processing_risks(treatment: dict) -> dict:
    """Analiza un tratamiento y sugiere riesgos para DPIA.

    El agente recibe el tratamiento completo (Art. 30) como contexto
    y genera una lista de riesgos potenciales con severidad estimada.
    El resultado SIEMPRE requiere validación del DPO.
    """

    # Construir contexto con datos del tratamiento
    context = f"""Analiza el siguiente tratamiento de datos personales
y genera una lista de riesgos para los derechos y libertades
de los interesados, según el Art. 35.7.b del RGPD.

Tratamiento: {treatment['name']}
Finalidades: {treatment['purposes']}
Base jurídica: {treatment['legal_basis']}
Categorías de datos: {treatment['personal_data_categories']}
Datos sensibles (Art. 9): {treatment['special_categories']}
Transferencias internacionales: {treatment['international_transfers']}
Destinatarios: {treatment['recipients']}

Para cada riesgo identificado, indica:
1. Descripción del riesgo
2. Derechos afectados (privacidad, no discriminación, etc.)
3. Probabilidad estimada (baja, media, alta)
4. Impacto estimado (bajo, medio, alto, muy alto)
5. Medida de mitigación sugerida

IMPORTANTE: Este análisis es una asistencia inicial.
La evaluación definitiva la realiza el DPO con contexto organizativo."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": context}]
    )

    # El resultado se almacena como borrador pendiente de validación
    return {
        "status": "draft_pending_review",
        "analysis": message.content[0].text,
        "model_used": "claude-sonnet-4-6",
        "requires_dpo_validation": True
    }

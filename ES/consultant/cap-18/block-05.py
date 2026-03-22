# Extraído de: LibroConsultor/cap-18-onboarding.md
def pre_review_deliverable(
    deliverable_text: str,
    deliverable_type: str,  # "gap_analysis", "audit_report", "proposal_section"
    style_guide_chunks: list[str]
) -> dict:
    """Pre-revisión automatizada antes de enviar al senior."""
    review_prompt = f"""Revisa este borrador de {deliverable_type} producido por
un consultor junior. Compara contra los estándares de estilo de la práctica.

ESTÁNDARES DE ESTILO:
{chr(10).join(style_guide_chunks)}

BORRADOR:
{deliverable_text}

Revisa:
1. Formato: ¿sigue la estructura estándar del tipo de documento?
2. Completitud: ¿faltan secciones obligatorias?
3. Terminología: ¿usa los términos estándar de la práctica o introduce variantes?
4. Datos: ¿hay afirmaciones sin evidencia o datos sin fuente?
5. Calidad mínima: ¿está listo para revisión del senior o necesita más trabajo?

Genera:
- Lista de correcciones necesarias antes de enviar al senior (si las hay)
- Evaluación general: "listo para revisión" o "necesita más trabajo"
- Puntuación de calidad estimada (1-10)
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system="Eres un revisor de calidad de documentos de consultoría. "
               "Tu objetivo es ayudar al junior a mejorar su borrador "
               "ANTES de que llegue al senior. Sé específico y constructivo.",
        messages=[{"role": "user", "content": review_prompt}]
    )

    return {
        "review": response.content[0].text,
        "ready_for_senior": "listo para revisión" in response.content[0].text.lower()
    }

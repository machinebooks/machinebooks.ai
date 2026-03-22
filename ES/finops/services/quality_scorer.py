# Extraído de: LibroFinOps/cap-21-aiact-auditoria.md
# services/quality_scorer.py
import anthropic

client = anthropic.Anthropic()


def auto_evaluate_compliance_report(
    report_text: str,
    normative_references: list,
) -> float:
    """
    Evalúa automáticamente un informe de cumplimiento.
    Verifica corrección de las citas normativas referenciadas.
    Coste estimado: ~$0.002 por evaluación con claude-haiku-4-5.
    """
    references_str = "\n".join(f"- {ref}" for ref in normative_references)
    prompt = f"""Evalúa esta respuesta de IA en escala 0.0-1.0.

Criterios:
1. Cita correctamente: {references_str}
2. Sin afirmaciones factuales incorrectas
3. Completo y bien estructurado

Respuesta a evaluar:
{report_text[:2000]}

Responde SOLO con un número entre 0.0 y 1.0."""

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=10,
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        return float(response.content[0].text.strip())
    except ValueError:
        return 0.5  # valor neutral si la evaluación falla

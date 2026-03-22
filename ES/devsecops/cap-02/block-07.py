# Extraído de: LibroDevSecOps/cap-02-anatomia-vulnerabilidad.md
import anthropic

client = anthropic.Anthropic()

def generate_pr_comment(triaged_findings: list[dict]) -> str:
    """Genera el comentario de PR con hallazgos priorizados."""

    critical_high = [f for f in triaged_findings
                     if f["risk_level"] in ("CRITICAL", "HIGH")]
    medium = [f for f in triaged_findings
              if f["risk_level"] == "MEDIUM"]
    low_fp = [f for f in triaged_findings
              if f["risk_level"] in ("LOW", "FALSE_POSITIVE")]

    prompt = f"""Genera un comentario de PR en Markdown que resuma los hallazgos
de seguridad. Sé directo y accionable.

Hallazgos CRITICAL/HIGH ({len(critical_high)}):
{json.dumps(critical_high, indent=2)}

Hallazgos MEDIUM ({len(medium)}):
{json.dumps(medium, indent=2)}

Hallazgos LOW/FALSE_POSITIVE descartados: {len(low_fp)}

Formato del comentario:
- Empieza con un resumen de una línea (bloqueante o no bloqueante)
- Lista los CRITICAL/HIGH con fichero, línea, descripción y fix sugerido
- Lista los MEDIUM como advertencias
- Indica cuántos se descartaron como bajo riesgo o falso positivo
- Cierra con el esfuerzo total estimado de remediación"""

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text

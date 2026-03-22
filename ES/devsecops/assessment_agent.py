# Extraído de: LibroDevSecOps/cap-25-madurez-devsecops.md
# assessment_agent.py — Agente Claude para evaluación automatizada de madurez
import anthropic
import json

client = anthropic.Anthropic()

ASSESSMENT_SYSTEM_PROMPT = """Eres un evaluador de madurez DevSecOps. Tu función es analizar
evidencias técnicas (configuraciones de CI/CD, logs, métricas, políticas) y determinar si
un criterio de madurez se cumple o no.

Reglas:
1. Responde SOLO con JSON: {"met": true/false, "evidence": "descripción de la evidencia",
   "confidence": "high/medium/low", "recommendation": "si no se cumple, qué hacer"}
2. Un criterio se cumple SOLO si la evidencia es clara e inequívoca.
3. "Parcialmente implementado" es NO cumplido. Sin ambiguedad.
4. Si la evidencia es insuficiente para determinar, responde met: false con confidence: low.
"""

def assess_criterion_with_agent(
    criterion_id: str,
    criterion_description: str,
    evidence_data: str,        # Configuración, logs o métricas relevantes
) -> dict:
    """Usa Claude para evaluar un criterio con base en evidencia técnica."""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=ASSESSMENT_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Criterio: {criterion_id} — {criterion_description}

Evidencia proporcionada:
{evidence_data}

¿Se cumple este criterio? Analiza la evidencia y responde en JSON."""
        }]
    )
    return json.loads(message.content[0].text)

# Ejemplo: verificar si SAST se ejecuta en cada PR
workflow_yaml = """
name: Security Scan
on:
  pull_request:
    branches: [main, develop]
jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/owasp-top-ten
            .semgrep/custom-rules/
"""

result = assess_criterion_with_agent(
    "PS-2.1",
    "¿El escaneo SAST se ejecuta en cada PR automáticamente?",
    f"Workflow de GitHub Actions:\n{workflow_yaml}"
)
# Resultado esperado: {"met": true, "evidence": "Workflow con trigger on pull_request
#   ejecuta Semgrep con reglas OWASP + custom", "confidence": "high", ...}

# Source: The FinOps Engineer and the Machine -- Chapter 25
# Pattern: Quality evaluation after optimization

# scripts/evaluar_calidad.py
# Uses claude-opus-4-6 as judge to evaluate relative quality.
# Judge cost: ~EUR 8-12/month for 5% output sampling.

import anthropic
import json


async def evaluar_con_juez(
    resultado_antes: str,
    resultado_despues: str,
    documento: str,
) -> dict:
    """Evaluates relative quality: previous system vs optimized."""
    client = anthropic.Anthropic()
    prompt = f"""Evaluate two analyses of the same document.
A = sistema anterior. B = sistema optimizado.

DOCUMENTO (muestra): {documento[:1500]}
ANALYSIS A: {resultado_antes[:1000]}
ANALYSIS B: {resultado_despues[:1000]}

Score precision and completeness (0-1).
JSON: {{"score_a": X.XX, "score_b": X.XX}}"""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=64,
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(response.content[0].text)

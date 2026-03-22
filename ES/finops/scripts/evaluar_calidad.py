# Extraído de: LibroFinOps/cap-25-caso-tokens.md
# scripts/evaluar_calidad.py
# Usa claude-opus-4-6 como juez para evaluar calidad relativa.
# Coste del juez: ~€8-12/mes por muestreo del 5% de outputs.

import anthropic
import json


async def evaluar_con_juez(
    resultado_antes: str,
    resultado_despues: str,
    documento: str,
) -> dict:
    """Evalúa calidad relativa: sistema anterior vs optimizado."""
    client = anthropic.Anthropic()
    prompt = f"""Evalúa dos análisis del mismo documento.
A = sistema anterior. B = sistema optimizado.

DOCUMENTO (muestra): {documento[:1500]}
ANÁLISIS A: {resultado_antes[:1000]}
ANÁLISIS B: {resultado_despues[:1000]}

Puntúa precisión y completitud (0-1).
JSON: {{"score_a": X.XX, "score_b": X.XX}}"""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=64,
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(response.content[0].text)

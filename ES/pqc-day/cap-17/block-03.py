# Extraído de: LibroPQC/cap-17-nist-pqc.md
# Ejemplo didáctico: patrones/ai_enrichment.py

import anthropic

def enrich_recommendation_with_context(
    finding: dict,
    code_context: str,
    nist_recommendation: str
) -> str:
    """
    Usa Claude para añadir contexto operativo a la recomendación
    NIST determinista.
    """
    client = anthropic.Anthropic()

    prompt = f"""Analiza este hallazgo criptográfico y enriquece la
recomendación de migración con contexto operativo específico.

HALLAZGO:
- Algoritmo: {finding['algorithm']}
- Fichero: {finding['file']}
- Línea: {finding['line']}
- Severidad: {finding['severity']}

CÓDIGO CIRCUNDANTE:
{code_context}

RECOMENDACIÓN BASE (determinista, no modificar):
{nist_recommendation}

INSTRUCCIONES:
1. Mantener la recomendación base tal cual.
2. Añadir contexto sobre el impacto operativo de la migración.
3. Identificar si el uso es para cifrado, firma o intercambio de claves.
4. Estimar la complejidad de la migración (baja/media/alta).
5. Señalar dependencias que podrían verse afectadas.
6. Si es código de test o ejemplo, indicar prioridad baja.

Responde en español. Sé conciso y práctico."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

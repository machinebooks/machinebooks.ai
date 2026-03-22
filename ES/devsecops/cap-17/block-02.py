# Extraído de: LibroDevSecOps/cap-17-aiact-pipeline.md
def classify_with_agent(manifest: dict) -> ClassificationResult:
    """Clasificación con Claude para casos que requieren interpretación."""
    client = anthropic.Anthropic()

    prompt = f"""Analiza el siguiente sistema de IA y clasifícalo según el
Reglamento (UE) 2024/1689 (AI Act).

MANIFIESTO DEL SISTEMA:
{yaml.dump(manifest, default_flow_style=False)}

CRITERIOS DE CLASIFICACIÓN:
- INACEPTABLE (Art. 5): puntuación social, manipulación subliminal,
  explotación de vulnerabilidades de grupos específicos, identificación
  biométrica remota en tiempo real en espacios públicos.
- ALTO RIESGO (Anexo III): sistemas en biometría, infraestructura
  crítica, educación, empleo, servicios esenciales, justicia,
  migración, procesos democráticos.
- LIMITADO (Art. 50): chatbots, deepfakes, sistemas de generación
  de contenido que requieren transparencia sobre la naturaleza IA.
- MÍNIMO: todos los demás.

RESPONDE en JSON con esta estructura exacta:
{{
  "risk_level": "unacceptable|high|limited|minimal",
  "confidence": 0.0-1.0,
  "rationale": "explicación en 2-3 frases",
  "applicable_articles": ["Art. X", ...],
  "obligations": ["obligación 1", ...],
  "requires_human_review": true/false
}}

Si la confianza es inferior a 0.7, marca requires_human_review como true."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parsear respuesta JSON y construir ClassificationResult
    import json
    result_data = json.loads(response.content[0].text)
    return ClassificationResult(
        risk_level=RiskLevel(result_data["risk_level"]),
        confidence=result_data["confidence"],
        rationale=result_data["rationale"],
        applicable_articles=result_data["applicable_articles"],
        obligations=result_data["obligations"],
        requires_human_review=result_data["requires_human_review"]
    )

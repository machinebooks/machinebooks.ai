# Extraído de: LibroDevSecOps/cap-03-mapa-superficie-ataque.md
"""
stride_classifier.py — Agente Claude que aplica STRIDE
a cada activo del inventario y genera un modelo de amenazas
priorizado por severidad y exposición.
"""
import anthropic
import json

STRIDE_CATEGORIES = [
    "Spoofing", "Tampering", "Repudiation",
    "Information Disclosure", "Denial of Service",
    "Elevation of Privilege"
]

SYSTEM_PROMPT = """Eres un analista de seguridad especializado en modelado
de amenazas STRIDE para sistemas con IA. Recibes un activo del inventario
del pipeline y debes evaluar cada categoría STRIDE.

Para cada categoría, responde con:
- applicable: true/false — ¿es esta amenaza relevante para este activo?
- severity: critical/high/medium/low — si es aplicable
- threat: descripción concisa de la amenaza específica (1-2 frases)
- mitigation: control técnico recomendado (1-2 frases)

Responde SOLO con JSON válido. No añadas explicaciones fuera del JSON.
Si el activo es de tipo llm_endpoint, rag_corpus o agent_tool,
presta especial atención a amenazas específicas de IA:
prompt injection, data poisoning, excessive agency.

Formato de respuesta:
{
  "asset": "<nombre del activo>",
  "threats": [
    {
      "stride_category": "<categoría>",
      "applicable": true,
      "severity": "high",
      "threat": "...",
      "mitigation": "..."
    }
  ]
}"""

def classify_asset_threats(
    client: anthropic.Anthropic,
    asset: dict
) -> dict:
    """Envía un activo al agente Claude para clasificación STRIDE."""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": (
                f"Analiza este activo del inventario del pipeline:\n"
                f"
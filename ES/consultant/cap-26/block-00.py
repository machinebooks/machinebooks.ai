# Extraído de: LibroConsultor/cap-26-caso-seguridad.md
from anthropic import Anthropic
import json

client = Anthropic()

SYSTEM_PROMPT = """Eres un auditor senior de seguridad de la información
con experiencia en ISO 27001:2022 y ENS (categoría alta).

Analiza el documento proporcionado e identifica:
1. Controles ISO 27001:2022 (Anexo A) que el documento evidencia
2. Nivel de cumplimiento por control: completo, parcial, insuficiente
3. Brechas detectadas con descripción específica
4. Controles ENS relacionados (mapeados desde ISO 27001)

Responde en JSON estructurado. Sé específico: cita párrafos del
documento que justifiquen cada evaluación. Si un control no tiene
evidencia en este documento, no lo incluyas."""

def analyze_document(doc_text: str, doc_name: str) -> dict:
    """Analiza un documento contra controles ISO 27001 y ENS."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Documento: {doc_name}\n\n{doc_text}"
        }]
    )
    # Parsear respuesta JSON del agente
    findings = json.loads(response.content[0].text)
    findings["source_document"] = doc_name
    findings["model"] = response.model
    findings["tokens_used"] = response.usage.input_tokens + response.usage.output_tokens
    return findings

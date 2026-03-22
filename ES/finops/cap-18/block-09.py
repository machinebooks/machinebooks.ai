# Extraído de: LibroFinOps/cap-18-business-case-cfo.md
import anthropic

def generate_executive_narrative(
    summary_json: dict,
) -> str:
    """
    Genera el texto narrativo del informe ejecutivo
    a partir del JSON del BusinessCaseGenerator.
    """
    client = anthropic.Anthropic()

    prompt = f"""Genera un informe ejecutivo de 1 página en español
para el CFO a partir de estos datos financieros:

{summary_json}

Requisitos:
- Lenguaje financiero (EBITDA, OPEX, payback, NPV)
- Sin jerga técnica (tokens, modelos, prompts)
- Incluir limitaciones y asunciones
- Tono profesional, datos antes que adjetivos
- Máximo 400 palabras"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text

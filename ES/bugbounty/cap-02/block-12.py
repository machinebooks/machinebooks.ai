# Extraído de: LibroBugBounty/cap-02-stack-hunter.md
#!/usr/bin/env python3
"""
AnÃ¡lisis local con LM Studio para material sensible.
Nunca envÃ­a datos a la nube.
"""
import openai

# LM Studio expone API compatible en localhost
client = openai.OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"  # LM Studio no requiere API key real
)

def analyze_locally(binary_analysis: str, context: str) -> str:
    """Analiza resultados de forma local (pre-disclosure)."""
    response = client.chat.completions.create(
        model="qwen2.5-coder-32b-instruct",
        messages=[
            {"role": "system", "content":
                "Eres un analista de seguridad. Analiza los datos "
                "proporcionados e identifica vulnerabilidades. "
                "SÃ© especÃ­fico: CVSS score, CWE, impacto concreto."},
            {"role": "user", "content":
                f"Contexto: {context}\n\n"
                f"Datos del anÃ¡lisis:\n{binary_analysis}"}
        ],
        temperature=0.1,  # Determinismo para anÃ¡lisis tÃ©cnico
        max_tokens=4096,
    )
    return response.choices[0].message.content

# Ejemplo: analizar system prompt extraÃ­do (OPSEC)
extracted_prompt = open("/lab/results/extracted_system_prompt.txt").read()
analysis = analyze_locally(
    binary_analysis=extracted_prompt,
    context="System prompt extraÃ­do de una aplicaciÃ³n de IA. "
            "Identificar herramientas, capabilities y datos sensibles."
)
print(analysis)

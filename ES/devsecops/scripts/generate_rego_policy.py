# Extraído de: LibroDevSecOps/cap-21-policy-as-code.md
# scripts/generate_rego_policy.py
import anthropic

client = anthropic.Anthropic()

def generate_rego_policy(requirement: str, domain: str) -> str:
    """Genera borrador de política Rego a partir de requisito en lenguaje natural."""
    system_prompt = """Eres un experto en Open Policy Agent y Rego.
Genera políticas de seguridad en Rego siguiendo estas convenciones:
- Usa import future.keywords (in, if, contains)
- Genera reglas 'deny' para bloqueos y 'warn' para advisories
- Incluye mensajes descriptivos con sprintf
- Genera tests para cada regla
- Usa data.* para datos externos parametrizables
- Comenta cada regla con su propósito"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": (
                f"Dominio: {domain}\n"
                f"Requisito: {requirement}\n\n"
                "Genera la política Rego y los tests correspondientes."
            )
        }]
    )
    return message.content[0].text

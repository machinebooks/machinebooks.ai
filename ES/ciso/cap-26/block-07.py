# Extraído de: LibroCISO/cap-26-politicas-concienciacion.md
import anthropic

async def generate_policy_draft(
    category: str,
    organization_context: str,
    frameworks: list[str],
) -> str:
    """Genera un borrador de política de seguridad
    adaptado al contexto de la organización.

    El borrador necesita revisión humana antes de aprobación.
    """
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": f"""Genera un borrador de política de seguridad
para la categoría: {category}

Contexto de la organización: {organization_context}
Marcos normativos aplicables: {', '.join(frameworks)}

Requisitos:
- Estructura: propósito, alcance, roles, directrices,
  excepciones, sanciones, revisión
- Lenguaje formal pero accesible
- Referencias a los marcos aplicables
- Secciones específicas del sector

Formato: Markdown con secciones numeradas."""
        }]
    )
    return message.content[0].text


async def suggest_policy_update(
    current_content: str,
    regulatory_change: str,
) -> str:
    """Sugiere actualizaciones a una política existente
    basándose en un cambio normativo detectado.

    Integración con el módulo de vigilancia normativa (Cap. 27).
    """
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""Analiza esta política de seguridad actual
y sugiere cambios basándote en la actualización normativa detectada.

POLÍTICA ACTUAL:
{current_content[:3000]}

CAMBIO NORMATIVO:
{regulatory_change}

Indica qué secciones necesitan actualización,
qué texto concreto hay que modificar, y por qué."""
        }]
    )
    return message.content[0].text

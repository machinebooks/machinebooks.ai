# Extraído de: LibroTecnico/cap-15-interfaces-chat.md
import anthropic
import json
from models.user_memory import MemoryCategory

EXTRACTION_PROMPT = """Analiza la conversación y extrae unidades de información
persistente sobre el usuario que serían útiles en futuras conversaciones.

Categorías disponibles:
- preferences: preferencias de trabajo, estilo, formato de respuesta
- client_facts: datos concretos sobre clientes mencionados
- workflow_patterns: cómo trabaja habitualmente el usuario
- insights: conclusiones, aprendizajes, decisiones que el usuario tomó

Devuelve JSON con lista de memorias a extraer (máximo 3 por conversación):
[{"category": "...", "content": "..."}, ...]

Si no hay nada relevante a memorizar, devuelve lista vacía: []
Solo incluye información objetiva y verificada en la conversación.
No inventes ni inferencias especulativas."""

async def extract_memories_from_session(
    conversation_history: list[dict],
    client: anthropic.Anthropic
) -> list[dict]:
    """
    Al cerrar una sesión de chat, extrae automáticamente
    memorias relevantes para inyectar en sesiones futuras.
    """
    if len(conversation_history) < 4:
        # Conversaciones muy cortas raramente contienen memorias útiles
        return []

    # Los mensajes pasan por redact_pii_for_llm() antes de la extracción
    # para evitar que PII del usuario quede almacenada en memorias persistentes
    conversation_text = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in conversation_history[-20:]  # Solo últimos 20 turnos
    ])

    response = client.messages.create(
        model="claude-haiku-4-5",  # Modelo ligero para extracción
        max_tokens=500,
        system=EXTRACTION_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Conversación:\n{conversation_text}"
        }]
    )

    try:
        memories = json.loads(response.content[0].text)
        # Validar que las categorías son válidas
        valid_categories = {cat.value for cat in MemoryCategory}
        return [
            m for m in memories
            if m.get('category') in valid_categories
            and m.get('content')
            and len(m['content']) < 300  # Memorias compactas
        ]
    except (json.JSONDecodeError, KeyError):
        return []

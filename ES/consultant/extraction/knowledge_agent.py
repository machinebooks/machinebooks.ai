# Extraído de: LibroConsultor/cap-17-memoria-institucional.md
# extraction/knowledge_agent.py — Agente de extracción de conocimiento
import anthropic
import json

client = anthropic.Anthropic()

EXTRACTION_PROMPT = """Eres un analista de conocimiento de consultoría.
Tu tarea es extraer fragmentos de conocimiento reutilizable del siguiente texto.

Para cada fragmento, identifica:
1. TIPO: "decision" | "pattern" | "lesson" | "insight"
2. CONTEXTO: situación en la que se aplica (sector, tipo de proyecto, problema)
3. CONTENIDO: el conocimiento en sí, formulado de forma que sea útil fuera
   del proyecto original (sin nombres de clientes ni datos confidenciales)
4. RESULTADO: qué consecuencia tuvo (si se menciona)
5. CONDICIONES: cuándo aplica y cuándo NO aplica

Reglas:
- Extrae solo conocimiento reutilizable, no resúmenes descriptivos
- Anonimiza cualquier referencia a clientes o proyectos específicos
- Si el texto no contiene conocimiento reutilizable, devuelve lista vacía
- Máximo 5 fragmentos por chunk de texto
- Cada fragmento debe ser comprensible sin el documento original

Devuelve JSON con formato:
[{"type": "...", "context": "...", "content": "...",
  "result": "...", "conditions": "..."}]"""

def extract_knowledge(chunk_text: str, section_title: str) -> list[dict]:
    """Extrae fragmentos de conocimiento de un chunk de texto."""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"## Sección: {section_title}\n\n{chunk_text}"
        }],
        system=EXTRACTION_PROMPT,
        temperature=0.1  # Baja temperatura para extracción determinista
    )

    try:
        fragments = json.loads(message.content[0].text)
        # Filtrar fragmentos vacíos o de baja calidad
        return [f for f in fragments if _is_quality_fragment(f)]
    except json.JSONDecodeError:
        return []

def _is_quality_fragment(fragment: dict) -> bool:
    """Valida que un fragmento tiene la calidad mínima requerida."""
    required_fields = {"type", "context", "content"}
    if not required_fields.issubset(fragment.keys()):
        return False
    # El contenido debe tener sustancia (más de 30 palabras)
    if len(fragment["content"].split()) < 30:
        return False
    # Verificar que no contiene datos sensibles residuales
    sensitive_patterns = ["@", "http://", "https://", "192.168", "10.0."]
    return not any(p in fragment["content"] for p in sensitive_patterns)

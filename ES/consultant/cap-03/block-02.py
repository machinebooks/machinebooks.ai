# Extraído de: LibroConsultor/cap-03-consultor-potenciado.md
import anthropic
import json
from datetime import datetime

client = anthropic.Anthropic()

def search_knowledge_base(query: str, filters: dict = None) -> list[dict]:
    """Busca en el RAG de la práctica documentos relevantes.

    En producción, esta función consulta Qdrant con embeddings.
    Aquí simplificamos la interfaz para claridad didáctica.
    """
    # Implementación real: genera embedding de la query,
    # busca los K documentos más cercanos en Qdrant,
    # filtra por metadata (cliente, tipo, fecha)
    # y devuelve texto + score + metadata
    pass

def get_client_history(client_ref: str) -> dict:
    """Recupera el historial completo con un cliente."""
    results = search_knowledge_base(
        query=f"proyectos con {client_ref}",
        filters={"type": ["proposal", "report", "lessons_learned"]}
    )
    return {
        "projects": [r for r in results if r["type"] == "project"],
        "deliverables": [r for r in results if r["type"] == "report"],
        "lessons": [r for r in results if r["type"] == "lessons_learned"],
        "last_contact": max(
            (r["date"] for r in results), default=None
        )
    }

BRIEFING_SYSTEM_PROMPT = """Eres un analista de consultoría tecnológica
que prepara briefings para reuniones con clientes.

Tu trabajo: dado el contexto del cliente, el objetivo de la reunión
y el historial de la relación, generar un briefing estructurado
que permita al consultor senior llegar a la reunión preparado
para aportar valor desde el primer minuto.

Reglas:
- Sé específico, no genérico. "El cliente tiene dudas sobre DORA"
  no es útil. "El cliente debe cumplir DORA antes de enero 2027
  y su principal gap es la gestión de riesgo ICT de terceros" sí lo es.
- Incluye las preguntas que el cliente puede hacer y prepara respuestas.
- Señala los puntos de fricción conocidos de proyectos anteriores.
- Si no hay historial, indícalo y sugiere preguntas de descubrimiento.
- El tono es interno: directo, sin diplomacia innecesaria.
- Máximo 3 páginas. El consultor lo leerá en 10 minutos."""

def prepare_meeting_briefing(
    client_ref: str,
    meeting_objective: str,
    attendees: list[dict],
    additional_context: str = ""
) -> str:
    """Genera un briefing completo para una reunión con cliente."""

    # 1. Recuperar historial del cliente
    history = get_client_history(client_ref)

    # 2. Buscar normativa relevante para el sector
    regulatory_context = search_knowledge_base(
        query=f"regulación aplicable sector {client_ref}",
        filters={"type": ["regulation", "standard"]}
    )

    # 3. Construir contexto enriquecido para el agente
    context = f"""
CLIENTE: {client_ref}
OBJETIVO DE LA REUNIÓN: {meeting_objective}
FECHA: {datetime.now().strftime('%Y-%m-%d')}

ASISTENTES:
{json.dumps(attendees, indent=2, ensure_ascii=False)}

HISTORIAL CON EL CLIENTE:
- Proyectos anteriores: {len(history['projects'])}
- Último contacto: {history['last_contact']}
- Lecciones aprendidas relevantes:
{json.dumps(history['lessons'][:5], indent=2, ensure_ascii=False)}

CONTEXTO REGULATORIO RELEVANTE:
{json.dumps(regulatory_context[:3], indent=2, ensure_ascii=False)}

CONTEXTO ADICIONAL:
{additional_context}
"""

    # 4. Generar briefing con Claude
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=BRIEFING_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Genera el briefing para esta reunión:

{context}

Estructura del briefing:
1. Contexto del cliente (sector, tamaño, regulación, relación)
2. Objetivo y agenda sugerida (60 min)
3. Estado actual: qué sabemos y qué no
4. Nuestra posición y recomendación preliminar
5. Preguntas que debemos hacer
6. Preguntas que nos harán y respuestas preparadas
7. Riesgos y temas sensibles
8. Próximos pasos sugeridos"""
        }]
    )

    return message.content[0].text

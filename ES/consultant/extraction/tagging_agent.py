# Extraído de: LibroConsultor/cap-17-memoria-institucional.md
# extraction/tagging_agent.py — Agente de etiquetado automático
import anthropic
import json

client = anthropic.Anthropic()

# Taxonomía cerrada para sectores y dominios, abierta para tecnologías
TAXONOMY = {
    "sectors": [
        "publico", "financiero", "industrial",
        "sanitario", "tecnologico", "energia", "retail"
    ],
    "domains": [
        "seguridad", "arquitectura", "datos", "operaciones",
        "cumplimiento", "ia", "cloud", "devops"
    ],
    "project_types": [
        "auditoria", "consultoria", "implantacion",
        "formacion", "preventa", "assessment"
    ],
    "outcomes": ["exito", "parcial", "fallido", "desconocido"]
}

TAGGING_PROMPT = f"""Clasifica el siguiente fragmento de conocimiento
según esta taxonomía. Asigna uno o más valores por eje.

Taxonomía:
- sector: {TAXONOMY['sectors']}
- dominio: {TAXONOMY['domains']}
- tipo_proyecto: {TAXONOMY['project_types']}
- resultado: {TAXONOMY['outcomes']}
- tecnologias: [lista abierta — identifica tecnologías mencionadas]
- relevancia: 1-5 (5 = conocimiento reutilizable en muchos contextos)

Devuelve JSON estricto con estos campos."""

def tag_fragment(fragment: dict) -> dict:
    """Etiqueta un fragmento de conocimiento con metadatos."""
    message = client.messages.create(
        model="claude-haiku-4-5",  # Haiku para etiquetado: rápido y barato
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": json.dumps(fragment, ensure_ascii=False)
        }],
        system=TAGGING_PROMPT,
        temperature=0.0
    )

    tags = json.loads(message.content[0].text)

    # Validar contra taxonomía cerrada
    tags["sector"] = [s for s in tags.get("sector", [])
                      if s in TAXONOMY["sectors"]]
    tags["dominio"] = [d for d in tags.get("dominio", [])
                       if d in TAXONOMY["domains"]]

    return {**fragment, "tags": tags}

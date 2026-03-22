# Extraído de: LibroDevSecOps/cap-12-dast-inteligente.md
def generate_business_logic_sequences(
    api_surface: dict,
    domain_context: str,
) -> list[dict]:
    """Genera secuencias de peticiones para testing de lógica de negocio."""
    prompt = f"""Dado el siguiente contexto de la API, genera secuencias
de peticiones que prueben vulnerabilidades de lógica de negocio.

Endpoints disponibles:
{json.dumps([
    {"path": e["path"], "method": e["method"], "summary": e["summary"]}
    for e in api_surface["endpoints"]
], indent=2)}

Dominio: {domain_context}

Genera secuencias que prueben:
1. Salto de pasos en flujos multi-paso
2. Repetición de acciones que solo deberían ejecutarse una vez
3. Manipulación de estado entre pasos (race conditions)
4. Acceso a recursos en estado inconsistente

Cada secuencia debe incluir:
- Nombre descriptivo del test
- Lista ordenada de peticiones HTTP
- Condición de vulnerabilidad (qué respuesta indica el fallo)
- Severidad estimada

Responde en JSON."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(message.content[0].text)

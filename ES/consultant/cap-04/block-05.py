# Extraído de: LibroConsultor/cap-04-rag-conocimiento.md
client_anthropic = anthropic.Anthropic(api_key="<TU_ANTHROPIC_KEY>")


def extract_search_filters(query: str) -> dict:
    """Usa Claude para extraer filtros implícitos de la consulta."""
    response = client_anthropic.messages.create(
        model="claude-haiku-4-5",
        max_tokens=256,
        system=(
            "Extrae filtros de búsqueda de la consulta del usuario. "
            "Devuelve JSON con campos opcionales: "
            "tipo (propuesta|informe|metodologia|leccion), "
            "sector (publico|financiero|industrial|tecnologico), "
            "year_min (int), year_max (int), "
            "framework (ISO_27001|ENS|DORA|NIS2|AI_Act), "
            "resultado (ganada|perdida|cancelada). "
            "Solo incluye campos que se deduzcan de la consulta."
        ),
        messages=[{"role": "user", "content": query}]
    )
    import json
    try:
        return json.loads(response.content[0].text)
    except (json.JSONDecodeError, IndexError):
        return {}

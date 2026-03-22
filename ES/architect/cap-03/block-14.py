# Extraído de: LibroTecnico/cap-03-ecosistema-claude.md
def _sse(event_type, **kwargs):
    """Formatea un evento como línea SSE."""
    payload = {"type": event_type, **kwargs}
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

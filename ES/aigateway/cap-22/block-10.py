# Extraído de: LibroAIGateway/cap-22-governance-engine.md
def _strip_code_spans(text: str) -> str:
    text = _RE_FENCED_CODE.sub("", text)
    return _RE_CODE_SPAN.sub("", text)

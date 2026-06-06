# Extraído de: LibroAIGateway/cap-05-router-smart-select.md
def classify_complexity(messages: list[dict]) -> str:
    text = _extract_text(messages)
    estimated_tokens = len(text) // 4
    has_code = "```" in text
    many_turns = len(messages) > 6
    is_complex_task = bool(_COMPLEX_PATTERNS.search(text))

    if estimated_tokens > 1500 or has_code or many_turns or is_complex_task:
        return "complex"

    is_simple_question = bool(_SIMPLE_PATTERNS.search(text.strip()[:200]))
    if estimated_tokens < 300 and is_simple_question:
        return "simple"

    return "medium"

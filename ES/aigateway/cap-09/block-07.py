# Extraído de: LibroAIGateway/cap-09-compresion-tokens.md
# gateway/app/services/compression/message_stubbing.py:61-70
def stub_message(message: dict, key: str) -> dict:
    content = _extract_text(message.get("content"))
    line_count = content.count("\n") + 1
    ctype = detect_content_type(content)
    stub = (
        f"[Compressed: {key} — {line_count} lines, {ctype}. "
        f"Use n7x_content_retrieve tool to get full content.]"
    )
    return {**message, "content": stub}

# Extraído de: LibroAIGateway/cap-09-compresion-tokens.md
# gateway/app/services/token_counter.py:94-123 (sintetizado)
def count_messages_tokens(messages: list[dict], model: str | None = None) -> int:
    encoding = _get_encoding(model)
    total = 0
    for msg in messages:
        total += _TOKENS_PER_MESSAGE          # 3 tokens por mensaje
        total += _count_string(encoding, str(msg.get("role")))
        total += _content_tokens(encoding, msg.get("content"))
        if msg.get("name"):
            total += _count_string(encoding, str(msg["name"]))
        if msg.get("tool_calls"):
            total += _count_string(encoding, json.dumps(msg["tool_calls"]))
    total += _TOKENS_PER_REPLY               # 3 tokens reply prime
    return total

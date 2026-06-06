# Extracted from: LibroAIGateway/cap-09-compression-tokens.md
# gateway/app/services/compression/smart_compression.py:76-84
async def should_compress(messages: list[dict], model: str) -> bool:
    trigger = int(get_system_infra_value("smart_compression_trigger_tokens", 100000))
    if trigger <= 0:
        return False  # kill-switch: 0 = disabled
    tokens = count_messages_tokens(messages, model)
    return tokens >= trigger

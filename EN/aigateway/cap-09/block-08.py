# Extracted from: LibroAIGateway/cap-09-compression-tokens.md
# gateway/app/services/compression/message_stubbing.py:38-58
def extract_key(message: dict, fallback_index: int, used_keys: Set[str]) -> str:
    content = _extract_text(message.get("content"))
    key = None
    for pattern in _FILE_PATH_PATTERNS:  # # filename, // filename, `file.ext`
        match = pattern.search(content[:2000])
        if match:
            key = match.group(1).split("/")[-1]
            break
    if key is None:
        key = f"message_{fallback_index}"
    # Avoid collisions: key, key_2, key_3...
    while key in used_keys:
        key = f"{base_key}_{counter}"
    used_keys.add(key)
    return key

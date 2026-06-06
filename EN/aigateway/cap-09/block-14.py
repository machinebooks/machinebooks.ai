# Extracted from: LibroAIGateway/cap-09-compression-tokens.md
# gateway/app/services/token_counter.py:55-64
def _count_string(encoding, text: str) -> int:
    if not text:
        return 0
    if encoding is None:
        # Heuristic fallback: 1 token ≈ 4 chars
        return max(1, (len(text) + 3) // 4)
    try:
        return len(encoding.encode(text))
    except Exception:
        return max(1, (len(text) + 3) // 4)

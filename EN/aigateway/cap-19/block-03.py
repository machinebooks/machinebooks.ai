# Extracted from: LibroAIGateway/cap-19-threat-jailbreak-dlp-pii.md
# NFKC normalization + zero-width strip (jailbreak_detector.py:33-51)
def _normalize_for_scan(text: str) -> str:
    # NFKC: fullwidth 'ignore' -> standard 'ignore', cyrillic -> latin
    normalized = unicodedata.normalize("NFKC", text)
    # Remove zero-width: U+200B, U+200C, U+200D, U+FEFF, U+2060
    invisibles = ("\u200b", "\u200c", "\u200d", "\ufeff", "\u2060")
    for ch in invisibles:
        normalized = normalized.replace(ch, "")
    return normalized

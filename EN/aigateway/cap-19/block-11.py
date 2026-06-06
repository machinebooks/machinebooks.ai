# Extracted from: LibroAIGateway/cap-19-threat-jailbreak-dlp-pii.md
# Classification with anti-ReDoS cap (dlp_service.py:184-263)
async def classify(text, db, organization_id=None):
    # Length cap: limits catastrophic backtracking in regex
    MAX_SCAN_CHARS = 50_000
    if len(text) > MAX_SCAN_CHARS:
        text = text[:MAX_SCAN_CHARS]

    # Sequential evaluation by level (secret → confidential → internal)
    for regex, tag in _SECRET_RE:
        if regex.search(text):
            level = max(level, "secret")
            indicators.append(tag)

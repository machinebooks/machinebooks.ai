# Extraído de: LibroAIGateway/cap-19-threat-jailbreak-dlp-pii.md
# Clasificación con cap anti-ReDoS (dlp_service.py:184-263)
async def classify(text, db, organization_id=None):
    # Cap de longitud: limita backtracking catastrophic en regex
    MAX_SCAN_CHARS = 50_000
    if len(text) > MAX_SCAN_CHARS:
        text = text[:MAX_SCAN_CHARS]

    # Evaluación secuencial por nivel (secret → confidential → internal)
    for regex, tag in _SECRET_RE:
        if regex.search(text):
            level = max(level, "secret")
            indicators.append(tag)

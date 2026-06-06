# Extracted from: LibroAIGateway/cap-22-governance-engine.md
_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|your)\s+instructions",
    r"jailbreak",
    r"DAN\s+mode",
    r"<\s*script",
    r"system\s*prompt\s*:",
    # ... patterns in Spanish and English
]

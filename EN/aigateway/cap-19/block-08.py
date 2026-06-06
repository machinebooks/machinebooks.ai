# Extracted from: LibroAIGateway/cap-19-threat-jailbreak-dlp-pii.md
# Role-switching detection (msj_defense_service.py:147-157)
_ROLE_SWITCH_PATTERNS = [
    re.compile(r"you\s+are\s+now\s+(DAN|unrestricted|evil|jailbroken)", re.I),
    re.compile(r"(enter|switch to|activate)\s+(DAN|developer|god)\s+mode", re.I),
    re.compile(r"from\s+now\s+on[\s,]+you\s+(will|must)\s+(always|never)", re.I),
]

for content in user_messages:
    for pattern in _ROLE_SWITCH_PATTERNS:
        if pattern.search(content):
            raise PolicyBlocked("Role-switching attempt detected")

# Extraído de: LibroAIGateway/cap-19-threat-jailbreak-dlp-pii.md
# Pesos por patrón (gateway/app/services/jailbreak_detector.py)
_RULES: List[_Rule] = [
    # prompt_override: peso 70 — fuerte, raro en uso legítimo
    _Rule(_compile(r"\bignor(?:e|a|es)\s+(?:all\s+|todas?\s+)?"
                  r"(?:(?:previous|the)\s+)?(?:instructions?)\b"),
          "prompt_override", 70),

    # role_bypass: peso 90 — crítico, casi exclusivo de ataques
    _Rule(_compile(r"\byou\s+are\s+(?:now|a|an)\s+"
                  r"(?:DAN|STAN|DUDE|unrestricted|jailbroken)"),
          "role_bypass", 90),

    # system_leak: peso 85
    _Rule(_compile(r"\b(?:show|tell|reveal|print|output|repeat|give)\s+"
                  r"(?:me\s+)?(?:your|the)\s+(?:system\s+)?(?:prompt|instructions?)\b"),
          "system_leak", 85),
]

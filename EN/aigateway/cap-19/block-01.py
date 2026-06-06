# Extracted from: LibroAIGateway/cap-19-threat-jailbreak-dlp-pii.md
# Weights per pattern (gateway/app/services/jailbreak_detector.py)
_RULES: List[_Rule] = [
    # prompt_override: weight 70 — strong, rare in legitimate use
    _Rule(_compile(r"\bignor(?:e|a|es)\s+(?:all\s+|todas?\s+)?"
                  r"(?:(?:previous|the)\s+)?(?:instructions?)\b"),
          "prompt_override", 70),

    # role_bypass: weight 90 — critical, almost exclusive to attacks
    _Rule(_compile(r"\byou\s+are\s+(?:now|a|an)\s+"
                  r"(?:DAN|STAN|DUDE|unrestricted|jailbroken)"),
          "role_bypass", 90),

    # system_leak: weight 85
    _Rule(_compile(r"\b(?:show|tell|reveal|print|output|repeat|give)\s+"
                  r"(?:me\s+)?(?:your|the)\s+(?:system\s+)?(?:prompt|instructions?)\b"),
          "system_leak", 85),
]

# Extracted from: LibroAISafety/ch-13-prompt-injection.md
# Didactic example of a prompt injection detector in input
# This code illustrates the concept — a production detector
# requires a trained classifier, not static rules

import re
from dataclasses import dataclass

@dataclass
class InjectionAnalysis:
    is_suspicious: bool
    confidence: float        # 0.0-1.0
    patterns_matched: list[str]
    recommendation: str      # "block", "flag", "allow"

def analyze_input(text: str) -> InjectionAnalysis:
    """
    Basic injection pattern analysis.
    A production system would use an ML classifier,
    not regex rules.
    """
    suspicious_patterns = [
        (r"ignore\s+(all\s+)?(previous\s+)?instructions",
         "override_instructions"),
        (r"(system\s*prompt|system\s+instructions)",
         "system_prompt_reference"),
        (r"(you\s+are|act\s+as|pretend\s+to\s+be)\s+a",
         "role_assignment"),
        (r"(forget|discard|ignore)\s+(everything|the\s+rules)",
         "rule_dismissal"),
    ]

    matches = []
    for pattern, name in suspicious_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            matches.append(name)

    if len(matches) >= 2:
        return InjectionAnalysis(
            is_suspicious=True,
            confidence=0.7,
            patterns_matched=matches,
            recommendation="block"
        )
    elif len(matches) == 1:
        return InjectionAnalysis(
            is_suspicious=True,
            confidence=0.4,
            patterns_matched=matches,
            recommendation="flag"  # Human review
        )
    return InjectionAnalysis(
        is_suspicious=False,
        confidence=0.3,
        patterns_matched=[],
        recommendation="allow"
    )

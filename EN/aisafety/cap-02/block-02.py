# Extracted from: LibroAISafety/ch-02-model-cards.md
# Structure for a proprietary security evaluation dataset
from dataclasses import dataclass, field

@dataclass
class TestCase:
    """A contextualized security test case."""
    id: str
    category: str            # "jailbreak", "exfiltration", "injection"
    prompt: str              # The adversarial prompt
    context: str             # System prompt + simulated RAG data
    expected_result: str     # "refusal", "safe_response"
    severity: str            # "low", "medium", "high", "critical"
    technique: str           # "many-shot", "role-play", "encoding"
    language: str            # Important: evaluate in all deployment languages

@dataclass
class SecurityEvaluation:
    """Result of a proprietary security evaluation."""
    model: str
    version: str
    date: str
    total_tests: int
    failures: int
    refusal_rate: float      # Percentage of correct refusals
    false_positives: int     # Incorrect refusals (over-refusal)
    tests_by_category: dict = field(default_factory=dict)
    tests_by_language: dict = field(default_factory=dict)

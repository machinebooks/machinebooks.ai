# Extracted from: LibroAIGateway/cap-20-classification-guardrails-firewall.md
# gateway/app/services/content_classifier_service.py:36-45

@dataclass
class ClassificationResult:
    """Content classification result."""
    matches: list[dict] = field(default_factory=list)
    risk_score: int = 0
    blocked: bool = False
    block_reason: str | None = None

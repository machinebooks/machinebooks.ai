# Extraído de: LibroAIGateway/cap-20-clasificacion-guardrails-firewall.md
# gateway/app/services/content_classifier_service.py:36-45

@dataclass
class ClassificationResult:
    """Resultado de la clasificación de contenido."""
    matches: list[dict] = field(default_factory=list)
    risk_score: int = 0
    blocked: bool = False
    block_reason: str | None = None

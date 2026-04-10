# Extracted from: LibroAISafety/ch-18-rag-security.md
# document_classifier.py — Pre-ingestion classification
import re
from dataclasses import dataclass

@dataclass
class ClassificationResult:
    """Result of document classification."""
    classification: str       # PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
    pii_types_found: list[str]
    sensitivity_signals: list[str]
    confidence: float         # 0.0 - 1.0
    requires_human_review: bool

class DocumentClassifier:
    """Classifies documents before RAG ingestion."""

    SENSITIVITY_SIGNALS = {
        "CONFIDENTIAL": [
            r"(?i)confidential", r"(?i)internal\s+use",
            r"(?i)do\s+not\s+distribute", r"(?i)draft",
        ],
        "RESTRICTED": [
            r"(?i)top\s+secret", r"(?i)restricted",
            r"(?i)classified", r"(?i)need.to.know",
        ],
    }

    def classify(self, text: str, source: str,
                 pii_found: list[str]) -> ClassificationResult:
        """Classifies a document by sensitivity."""
        signals = []
        classification = "PUBLIC"

        # Classify by text signals
        for level, patterns in self.SENSITIVITY_SIGNALS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    signals.append(f"{level}: {pattern}")
                    if level == "RESTRICTED":
                        classification = "RESTRICTED"
                    elif classification != "RESTRICTED":
                        classification = "CONFIDENTIAL"

        # Elevate classification if PII found
        if pii_found and classification == "PUBLIC":
            classification = "CONFIDENTIAL"
            signals.append("PII detected: elevated to CONFIDENTIAL")

        # Low confidence if no clear signals
        confidence = 0.9 if signals else 0.5
        needs_review = confidence < 0.7 or classification == "RESTRICTED"

        return ClassificationResult(
            classification=classification,
            pii_types_found=pii_found,
            sensitivity_signals=signals,
            confidence=confidence,
            requires_human_review=needs_review,
        )

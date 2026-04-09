# Extraido de: LibroAISafety/cap-18-rag-seguridad.md
# document_classifier.py — Clasificación pre-ingestión
import re
from dataclasses import dataclass

@dataclass
class ClassificationResult:
    """Resultado de la clasificación de un documento."""
    classification: str       # PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
    pii_types_found: list[str]
    sensitivity_signals: list[str]
    confidence: float         # 0.0 - 1.0
    requires_human_review: bool

class DocumentClassifier:
    """Clasifica documentos antes de la ingestión en RAG."""

    SENSITIVITY_SIGNALS = {
        "CONFIDENTIAL": [
            r"(?i)confidencial", r"(?i)uso\s+interno",
            r"(?i)no\s+distribuir", r"(?i)draft|borrador",
        ],
        "RESTRICTED": [
            r"(?i)top\s+secret", r"(?i)restringido",
            r"(?i)clasificado", r"(?i)need.to.know",
        ],
    }

    def classify(self, text: str, source: str,
                 pii_found: list[str]) -> ClassificationResult:
        """Clasifica un documento por sensibilidad."""
        signals = []
        classification = "PUBLIC"

        # Clasificar por señales de texto
        for level, patterns in self.SENSITIVITY_SIGNALS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    signals.append(f"{level}: {pattern}")
                    if level == "RESTRICTED":
                        classification = "RESTRICTED"
                    elif classification != "RESTRICTED":
                        classification = "CONFIDENTIAL"

        # Elevar clasificación si hay PII
        if pii_found and classification == "PUBLIC":
            classification = "CONFIDENTIAL"
            signals.append("PII detectada: elevado a CONFIDENTIAL")

        # Confianza baja si no hay señales claras
        confidence = 0.9 if signals else 0.5
        needs_review = confidence < 0.7 or classification == "RESTRICTED"

        return ClassificationResult(
            classification=classification,
            pii_types_found=pii_found,
            sensitivity_signals=signals,
            confidence=confidence,
            requires_human_review=needs_review,
        )

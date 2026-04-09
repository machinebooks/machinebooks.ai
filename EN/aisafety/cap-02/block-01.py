# Extracted from: LibroAISafety/ch-02-model-cards.md
from dataclasses import dataclass
from datetime import date

@dataclass
class ModelCardDiscrepancy:
    """Records a discrepancy between what the Model Card
    claims and what external evidence demonstrates."""
    model: str
    model_card_claim: str    # Model Card assertion
    external_evidence: str   # Paper, report, or proprietary test
    source: str              # URL or paper reference
    discovery_date: date
    severity: str            # "info", "warning", "critical"
    deployment_impact: str   # How it affects our system

# Real example
discrepancy = ModelCardDiscrepancy(
    model="example-model-v2",
    model_card_claim="Harmful content refusal rate: 96.2%",
    external_evidence="Many-shot technique with 256 examples: "
                      "38% success in restricted categories",
    source="Anil et al., 2024 — Many-shot Jailbreaking",
    discovery_date=date(2026, 3, 15),
    severity="critical",
    deployment_impact="Our system allows long contexts "
                      "for document analysis — exposed surface"
)

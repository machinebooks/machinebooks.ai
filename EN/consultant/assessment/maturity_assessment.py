# Source: The Consultant and the Machine -- Chapter 15
# Pattern: AI maturity assessment with adaptive interviews
import anthropic
from dataclasses import dataclass, field
from enum import Enum

class Dimension(str, Enum):
    STRATEGY = "estrategia"
    DATA = "datos"
    TECHNOLOGY = "tecnologia"
    PEOPLE = "personas"
    GOVERNANCE = "gobernanza"

@dataclass
class AssessmentQuestion:
    id: str
    dimension: Dimension
    text: str
    stakeholder_profiles: list[str]  # CIO, CDO, business, IT, etc.
    evidence_required: bool = False
    follow_ups: list[str] = field(default_factory=list)

# Partial catalog — the real one has 85 questions
QUESTION_CATALOG = [
    AssessmentQuestion(
        id="STR-01",
        dimension=Dimension.STRATEGY,
        text="Does an AI strategy document approved by "
             "management exist? Who created it and when?",
        stakeholder_profiles=["CIO", "CEO", "CDO"],
        evidence_required=True,
        follow_ups=[
            "Is it reviewed periodically? How often?",
            "Does it have allocated budget or is it declarative?",
            "What success metrics does it define?"
        ]
    ),
    AssessmentQuestion(
        id="DAT-01",
        dimension=Dimension.DATA,
        text="Do you have an updated data catalog? "
             "What percentage of your data sources are documented?",
        stakeholder_profiles=["CDO", "CIO", "IT"],
        evidence_required=True,
        follow_ups=[
            "Do you have automated data quality metrics?",
            "How long does it take a new team to access "
             "the data they need?"
        ]
    ),
]

# --- Block 2 ---

from dataclasses import dataclass

@dataclass
class DimensionScore:
    dimension: Dimension
    level: float          # 1.0 - 5.0, with decimals
    confidence: float     # 0.0 - 1.0
    evidence_ratio: float # Proportion of responses with evidence
    key_findings: list[str]
    gaps: list[str]
    strengths: list[str]

@dataclass
class MaturityAssessment:
    organization: str
    sector: str
    size_band: str          # "200-500", "500-2000", "2000+"
    assessment_date: str
    dimensions: list[DimensionScore]
    overall_level: float
    stakeholders_interviewed: int

    @property
    def overall_level_weighted(self) -> float:
        """Weighted overall level — data and people weigh more."""
        weights = {
            Dimension.STRATEGY: 0.15,
            Dimension.DATA: 0.25,      # Higher weight: no data, no AI
            Dimension.TECHNOLOGY: 0.20,
            Dimension.PEOPLE: 0.25,    # Higher weight: no people, no change
            Dimension.GOVERNANCE: 0.15,
        }
        total = sum(
            d.level * weights[d.dimension] for d in self.dimensions
        )
        return round(total, 1)

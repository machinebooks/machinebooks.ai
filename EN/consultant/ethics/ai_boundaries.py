# Source: The Consultant and the Machine -- Chapter 24
# Pattern: AI boundaries: validation, fasting, decision matrix
from anthropic import Anthropic
from dataclasses import dataclass
from enum import Enum

class VerifiabilityLevel(Enum):
    FACTUAL = "factual"          # Verifiable datum: article, date, figure
    ANALYTICAL = "analytical"     # Conclusion derived from data
    JUDGMENTAL = "judgmental"      # Judgment requiring human context
    SPECULATIVE = "speculative"   # Prediction or extrapolation

@dataclass
class Claim:
    text: str
    level: VerifiabilityLevel
    source_required: bool
    verified: bool = False

def classify_claims(document_text: str) -> list[Claim]:
    """Extracts and classifies claims from an AI-generated document.

    FACTUAL claims require mandatory verification.
    JUDGMENTAL claims require review by a domain senior.
    SPECULATIVE claims are flagged for editorial decision."""

    client = Anthropic()

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system="""Analyze the text and extract each claim, classifying it:
        - FACTUAL: regulatory references, statistics, dates, names
        - ANALYTICAL: conclusions derived from presented data
        - JUDGMENTAL: assessments depending on undocumented context
        - SPECULATIVE: predictions or extrapolations without empirical basis
        Return JSON with: text, level, source_required (true if FACTUAL)""",
        messages=[{"role": "user", "content": document_text}]
    )

    # Parse response and build claims list
    # FACTUAL claims enter mandatory verification queue
    # JUDGMENTAL claims are escalated to the project senior
    return parse_claims(response.content[0].text)

# --- Block 2 ---

from datetime import date, timedelta
from dataclasses import dataclass

@dataclass
class DigitalFastingPolicy:
    """Digital fasting policy to maintain baseline skills.

    Each consultant dedicates regulated time to work without AI
    assistance to preserve autonomous analysis and writing capacity."""

    # One day per month without AI tools for analytical tasks
    monthly_fast_day: int = 15  # Day of month

    # Each new proposal: first approach draft WITHOUT AI
    proposal_first_draft_manual: bool = True

    # Client diagnostic meetings: no AI preparation
    diagnostic_meetings_manual: bool = True

    # Deliverable review: at least one review without AI suggestions
    final_review_manual: bool = True

    def should_use_ai(self, task_type: str, current_date: date) -> dict:
        """Determines whether a task should be done with or without AI."""
        is_fast_day = current_date.day == self.monthly_fast_day

        rules = {
            "proposal_approach": {
                "ai_allowed": not self.proposal_first_draft_manual,
                "reason": "The first strategic draft exercises "
                         "the consultant's independent thinking"
            },
            "client_diagnostic": {
                "ai_allowed": not self.diagnostic_meetings_manual,
                "reason": "Reading the room and active listening "
                         "require complete human presence"
            },
            "deliverable_review": {
                "ai_allowed": not self.final_review_manual,
                "reason": "The final review must apply human judgment "
                         "without the model's confirmation bias"
            },
            "routine_analysis": {
                "ai_allowed": not is_fast_day,
                "reason": "Digital fasting day: analytical tasks "
                         "without AI assistance" if is_fast_day else "OK"
            }
        }

        return rules.get(task_type, {
            "ai_allowed": not is_fast_day,
            "reason": "General policy"
        })

# --- Block 3 ---

from enum import Enum
from dataclasses import dataclass

class AIZone(Enum):
    GREEN = "green"    # AI recommended: data analysis, drafts, search
    YELLOW = "yellow"  # AI as draft, mandatory deep human review
    ORANGE = "orange"  # AI only for supporting data, 100% human narrative
    RED = "red"        # AI prohibited: complete human presence

@dataclass
class TaskAssessment:
    zone: AIZone
    rationale: str
    review_required: str  # "none", "peer", "senior", "partner"

def assess_task(
    involves_crisis: bool,
    politically_sensitive: bool,
    ethical_ambiguity: bool,
    client_facing: bool,
    precedent_exists: bool,
    contractual_restriction: bool,
    data_verification_possible: bool
) -> TaskAssessment:
    """Evaluates the AI usage zone for a consulting task.

    Rule: a single red criterion sends the entire task to the red zone.
    Yellow criteria accumulate: two yellows bump up to orange."""

    # Red zone criteria (any one activates red zone)
    if contractual_restriction:
        return TaskAssessment(
            AIZone.RED,
            "Contractual restriction: AI prohibited",
            "partner"
        )
    if involves_crisis and client_facing:
        return TaskAssessment(
            AIZone.RED,
            "Crisis communication: human presence required",
            "partner"
        )
    if ethical_ambiguity and not precedent_exists:
        return TaskAssessment(
            AIZone.RED,
            "Ethical dilemma without precedent: exclusive human judgment",
            "partner"
        )

    # Orange zone criteria
    yellow_count = sum([
        politically_sensitive,
        client_facing and not data_verification_possible,
        not precedent_exists
    ])

    if yellow_count >= 2:
        return TaskAssessment(
            AIZone.ORANGE,
            "Multiple risk factors: AI only for data",
            "senior"
        )

    # Yellow zone criteria
    if politically_sensitive or client_facing:
        return TaskAssessment(
            AIZone.YELLOW,
            "Moderate sensitivity: AI draft + deep review",
            "senior"
        )

    # Green zone by default
    return TaskAssessment(
        AIZone.GREEN,
        "Standard analytical task: AI recommended",
        "peer"
    )

# --- Block 4 ---

from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class AIIncident:
    """Incident record for inappropriate AI use.

    Anonymous and learning-oriented, not blame-oriented.
    Reviewed monthly in the practice improvement meeting."""

    timestamp: datetime = field(default_factory=datetime.now)

    category: str = ""  # "hallucination", "overreliance", "wrong_zone",
                        # "client_trust", "quality_degradation"

    project_phase: str = ""  # "presale", "delivery", "review", "communication"

    impact: str = ""  # "none_detected", "rework_required",
                      # "client_dissatisfaction", "contract_loss"

    description: str = ""

    prevention: str = ""

    correct_zone: str = ""  # "green", "yellow", "orange", "red"
    actual_zone_used: str = ""

def analyze_incidents(incidents: list[AIIncident]) -> dict:
    """Generates quarterly incident report for practice improvement."""
    total = len(incidents)
    if total == 0:
        return {"message": "No incidents recorded"}

    by_category = {}
    by_impact = {}
    zone_mismatches = 0

    for inc in incidents:
        by_category[inc.category] = by_category.get(inc.category, 0) + 1
        by_impact[inc.impact] = by_impact.get(inc.impact, 0) + 1
        if inc.correct_zone != inc.actual_zone_used:
            zone_mismatches += 1

    return {
        "total_incidents": total,
        "by_category": by_category,
        "by_impact": by_impact,
        "zone_mismatch_rate": zone_mismatches / total,
        "preventable_rate": zone_mismatches / total
    }

# Source: The Consultant and the Machine -- Chapter 21
# Pattern: Service productization: assessment, monitoring
import anthropic
from dataclasses import dataclass, field
from enum import Enum

class MaturityLevel(Enum):
    AD_HOC = 1       # No defined processes
    EXPERIMENTAL = 2  # Isolated pilots
    OPERATIONAL = 3   # AI in production, specific cases
    OPTIMIZED = 4     # Integrated AI, metrics, governance
    TRANSFORMATIVE = 5 # AI as systemic competitive advantage

@dataclass
class DimensionScore:
    dimension: str          # "data", "talent", "governance", etc.
    score: float            # 1.0 to 5.0
    confidence: float       # 0.0 to 1.0 — low if inconsistencies
    inconsistencies: list   # Contradictory responses detected
    evidence_gaps: list     # Missing evidence for validation

@dataclass
class AssessmentResult:
    client_id: str
    dimensions: list[DimensionScore] = field(default_factory=list)
    overall_level: MaturityLevel = MaturityLevel.AD_HOC
    flags_for_consultant: list[str] = field(default_factory=list)

    def calculate_overall(self):
        """Overall level = weighted average, penalized by inconsistencies."""
        if not self.dimensions:
            return
        weighted_sum = sum(
            d.score * d.confidence for d in self.dimensions
        )
        total_confidence = sum(d.confidence for d in self.dimensions)
        avg = weighted_sum / total_confidence if total_confidence > 0 else 1.0
        self.overall_level = MaturityLevel(min(5, max(1, round(avg))))

        # Flag low-confidence dimensions for human review
        for d in self.dimensions:
            if d.confidence < 0.6:
                self.flags_for_consultant.append(
                    f"Dimension '{d.dimension}': confidence {d.confidence:.0%}. "
                    f"Inconsistencies: {', '.join(d.inconsistencies[:3])}"
                )

# --- Block 2 ---

client = anthropic.Anthropic()

def detect_inconsistencies(
    dimension: str,
    responses: list[dict]
) -> list[str]:
    """Detects contradictions in responses within a dimension."""
    responses_text = "\n".join(
        f"- Question: {r['question']}\n  Answer: {r['answer']}"
        for r in responses
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=(
            "You are an expert auditor of AI maturity. "
            "Analyze a client's responses and detect "
            "internal inconsistencies. An inconsistency is when "
            "two answers contradict or are incompatible. "
            "Return ONLY the inconsistencies found, "
            "one per line. If there are no inconsistencies, respond NONE."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Dimension: {dimension}\n\n"
                f"Client responses:\n{responses_text}\n\n"
                "List of detected inconsistencies:"
            )
        }]
    )

    result = message.content[0].text.strip()
    if result == "NONE":
        return []
    return [line.strip("- ") for line in result.split("\n") if line.strip()]

# --- Block 3 ---

from datetime import date

SECTOR_BENCHMARKS = {
    "financiero": {"datos": 3.8, "talento": 3.2, "gobernanza": 3.5,
                   "infraestructura": 3.6, "casos_uso": 3.1, "cultura": 2.8},
    "sector_publico": {"datos": 2.4, "talento": 2.1, "gobernanza": 2.8,
                       "infraestructura": 2.5, "casos_uso": 1.9, "cultura": 2.0},
    "industrial": {"datos": 2.9, "talento": 2.5, "gobernanza": 2.2,
                   "infraestructura": 3.0, "casos_uso": 2.6, "cultura": 2.3},
    "retail": {"datos": 3.2, "talento": 2.7, "gobernanza": 2.4,
               "infraestructura": 3.1, "casos_uso": 3.0, "cultura": 2.9},
}

def generate_executive_report(
    result: AssessmentResult,
    client_name: str,
    sector: str
) -> str:
    """Generates executive report with sector benchmarks."""
    benchmarks = SECTOR_BENCHMARKS.get(sector, {})

    comparisons = []
    for dim in result.dimensions:
        bench = benchmarks.get(dim.dimension, 0)
        delta = dim.score - bench
        position = "above" if delta > 0.3 else (
            "below" if delta < -0.3 else "in line with"
        )
        comparisons.append(
            f"- **{dim.dimension.capitalize()}**: {dim.score:.1f}/5.0 "
            f"({position} the sector average: {bench:.1f})"
        )

    comparisons_text = "\n".join(comparisons)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=(
            "You are a senior consultant specialized in AI adoption. "
            "Generate an executive AI maturity assessment report. "
            "Tone: professional, direct, action-oriented. "
            "Structure: executive summary (1 paragraph), findings per "
            "dimension (2-3 sentences each), top 3 recommendations "
            "prioritized by impact, and suggested next steps. "
            "Do NOT use empty jargon. Every recommendation must include "
            "an effort estimate (low/medium/high) and timeline."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Client: {client_name}\n"
                f"Sector: {sector}\n"
                f"Overall level: {result.overall_level.name} "
                f"({result.overall_level.value}/5)\n"
                f"Date: {date.today().isoformat()}\n\n"
                f"Scores vs sector benchmark:\n"
                f"{comparisons_text}\n\n"
                f"Inconsistencies detected:\n"
                + ("\n".join(result.flags_for_consultant)
                   if result.flags_for_consultant
                   else "None detected")
                + "\n\nGenerate the executive report."
            )
        }]
    )

    return message.content[0].text

# --- Block 4 ---

from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
from typing import Optional

class PlanType(Enum):
    SINGLE = "single"           # One assessment, no recurrence
    QUARTERLY = "quarterly"     # Assessment every 3 months + consultant
    CONTINUOUS = "continuous"   # Quarterly assessment + monitoring

@dataclass
class Subscription:
    client_id: str
    plan: PlanType
    start_date: date
    price_eur: float
    consultant_hours_included: float  # Consultant hours per period
    assessments_remaining: int
    next_assessment_date: Optional[date] = None

    @classmethod
    def create_quarterly(cls, client_id: str) -> "Subscription":
        """Quarterly plan: 4 assessments/year + 6h consultant."""
        return cls(
            client_id=client_id,
            plan=PlanType.QUARTERLY,
            start_date=date.today(),
            price_eur=4500.0,       # €4,500/year
            consultant_hours_included=6.0,  # Per quarter
            assessments_remaining=4,
            next_assessment_date=date.today() + timedelta(days=90),
        )

    @classmethod
    def create_continuous(cls, client_id: str) -> "Subscription":
        """Continuous plan: assessments + monitoring + 12h consultant."""
        return cls(
            client_id=client_id,
            plan=PlanType.CONTINUOUS,
            start_date=date.today(),
            price_eur=9600.0,       # €9,600/year (€800/month)
            consultant_hours_included=12.0,  # Per quarter
            assessments_remaining=4,
            next_assessment_date=date.today() + timedelta(days=90),
        )

    def is_assessment_due(self) -> bool:
        """Checks if it's time to run a new assessment."""
        if self.next_assessment_date is None:
            return False
        return date.today() >= self.next_assessment_date

    def record_assessment(self):
        """Records a completed assessment and schedules the next."""
        self.assessments_remaining -= 1
        if self.assessments_remaining > 0:
            self.next_assessment_date = date.today() + timedelta(days=90)
        else:
            self.next_assessment_date = None

def check_pending_assessments(
    subscriptions: list[Subscription]
) -> list[dict]:
    """Generates alerts for assessments that need to be executed."""
    alerts = []
    for sub in subscriptions:
        if sub.is_assessment_due():
            alerts.append({
                "client_id": sub.client_id,
                "plan": sub.plan.value,
                "action": "assessment_due",
                "message": (
                    f"Quarterly assessment pending. "
                    f"{sub.assessments_remaining} remaining in period."
                ),
            })
    return alerts

# --- Block 5 ---

from claude_agent_sdk import Agent, tool

@tool
def run_assessment(client_id: str, sector: str) -> dict:
    """Runs the complete assessment for a client."""
    # 1. Retrieve questionnaire responses (already completed online)
    responses = get_client_responses(client_id)

    # 2. Evaluate each dimension
    dimensions = [
        "datos", "talento", "gobernanza",
        "infraestructura", "casos_uso", "cultura"
    ]
    result = AssessmentResult(client_id=client_id)

    for dim in dimensions:
        dim_responses = [r for r in responses if r["dimension"] == dim]
        inconsistencies = detect_inconsistencies(dim, dim_responses)
        raw_score = calculate_dimension_score(dim_responses)
        confidence = max(0.3, 1.0 - len(inconsistencies) * 0.15)

        result.dimensions.append(DimensionScore(
            dimension=dim,
            score=raw_score,
            confidence=confidence,
            inconsistencies=inconsistencies,
            evidence_gaps=find_evidence_gaps(dim_responses),
        ))

    result.calculate_overall()

    # 3. Generate executive report
    report = generate_executive_report(
        result,
        client_name=get_client_name(client_id),
        sector=sector,
    )

    # 4. Save results and schedule consultant review
    save_assessment(client_id, result, report)
    schedule_consultant_review(client_id, result.flags_for_consultant)

    return {
        "overall_level": result.overall_level.name,
        "flags_count": len(result.flags_for_consultant),
        "report_generated": True,
        "consultant_review_scheduled": len(result.flags_for_consultant) > 0,
    }

# --- Block 6 ---

@dataclass
class ProductizationCandidate:
    service_name: str
    repetition_score: float    # 0-1: how many times have we done it?
    variability_score: float   # 0-1: how much does it change between clients?
    automation_potential: float # 0-1: what % of work is mechanical?
    demand_signal: float       # 0-1: do clients ask for it spontaneously?[^senal_demanda]

    @property
    def productization_score(self) -> float:
        """Productization index. >0.6 = viable candidate."""
        return (
            self.repetition_score * 0.30
            + (1 - self.variability_score) * 0.25  # Less variability = better
            + self.automation_potential * 0.25
            + self.demand_signal * 0.20
        )

candidates = [
    ProductizationCandidate(
        service_name="AI maturity assessment",
        repetition_score=0.9,     # 23 times in 18 months
        variability_score=0.3,    # Stable framework, minor adaptation
        automation_potential=0.75, # 38/60 hours automatable
        demand_signal=0.8,        # Clients proactively request it
    ),
    ProductizationCandidate(
        service_name="Compliance audit",
        repetition_score=0.85,
        variability_score=0.7,    # High: varies greatly by regulatory framework
        automation_potential=0.60,
        demand_signal=0.6,
    ),
    ProductizationCandidate(
        service_name="Continuous monitoring",
        repetition_score=0.2,     # Low: never sold it as such
        variability_score=0.5,
        automation_potential=0.85,
        demand_signal=0.9,        # Highly requested but didn't exist
    ),
]

for c in candidates:
    print(f"{c.service_name}: {c.productization_score:.2f}")
# AI maturity assessment: 0.77
# Compliance audit: 0.55
# Continuous monitoring: 0.58

# --- Block 7 ---

from claude_agent_sdk import Agent, tool
from datetime import datetime

@tool
def verify_control_evidence(
    control_id: str,
    framework: str,
    evidence_sources: list[str]
) -> dict:
    """Verifies whether a control's evidence is still valid."""
    evidence_data = collect_evidence(evidence_sources)

    message = client.messages.create(
        model="claude-haiku-4-5",  # Haiku for frequent verifications
        max_tokens=512,
        system=(
            f"You are a {framework} auditor. Evaluate whether the evidence "
            "presented demonstrates control compliance. "
            "Respond with: COMPLIANT, PARTIALLY_COMPLIANT or NON_COMPLIANT, "
            "followed by a one-sentence justification."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Control: {control_id}\n"
                f"Collected evidence:\n{evidence_data}\n"
                f"Verification date: {datetime.now().isoformat()}\n"
                "Evaluation:"
            )
        }]
    )

    response = message.content[0].text.strip()
    status = response.split(",")[0].strip() if "," in response else response.split()[0]

    return {
        "control_id": control_id,
        "framework": framework,
        "status": status,
        "justification": response,
        "verified_at": datetime.now().isoformat(),
        "cost_usd": 0.003,  # Estimated cost per verification with Haiku
    }

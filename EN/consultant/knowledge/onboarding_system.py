# Source: The Consultant and the Machine -- Chapter 18
# Pattern: Onboarding: mentoring agent, simulator, tracking
from dataclasses import dataclass, field
from enum import Enum

class ContentCategory(Enum):
    METHODOLOGY = "methodology"          # How we do things
    STANDARDS = "standards"              # What standards we apply
    TEMPLATES = "templates"              # Deliverable formats
    CASE_STUDIES = "case_studies"        # Examples from past projects
    TOOLS = "tools"                      # Tools and configurations
    CLIENT_PROTOCOLS = "client_protocols"  # Client interaction protocols

class DifficultyLevel(Enum):
    FOUNDATIONAL = 1    # What you need to know in the first week
    INTERMEDIATE = 2    # What you need for your first task
    ADVANCED = 3        # What you need to work unsupervised

@dataclass
class OnboardingDocument:
    """Document indexed for the onboarding program."""
    doc_id: str
    title: str
    category: ContentCategory
    difficulty: DifficultyLevel
    summary: str                              # 2-3 sentence summary
    prerequisites: list[str] = field(default_factory=list)  # IDs of prior docs
    estimated_read_time_min: int = 10
    last_updated: str = ""                    # Date of last review
    verified_by: str = ""                     # Senior who validated the content

# --- Block 2 ---

import anthropic
from qdrant_client import QdrantClient

# Connection to onboarding RAG
qdrant = QdrantClient(url="http://localhost:6333")
client = anthropic.Anthropic(api_key="<YOUR_ANTHROPIC_KEY>")

MENTOR_SYSTEM_PROMPT = """You are a technology consulting mentor. Your role is to help
junior consultants understand the consulting firm's methodologies, standards, and practices.

Rules:
1. Respond ONLY with information from the provided context (practice documents).
2. If you don't have sufficient information, say "I don't have documentation on this —
   ask your assigned mentor" and log the gap.
3. When citing a procedure, indicate the source document so the junior
   can read it in full.
4. Adapt the depth of the response to the junior's level (foundational,
   intermediate, advanced).
5. After answering, suggest 1-2 related documents that expand on the topic.
6. NEVER invent procedures or standards. If something isn't documented,
   it's a gap that should be escalated.
7. Include concrete examples when possible.

Junior's level: {difficulty_level}
Onboarding week: {onboarding_week}
Assigned project: {assigned_project_type}
"""

def query_mentor(
    question: str,
    junior_profile: dict,
    collection: str = "onboarding_docs"
) -> dict:
    """Queries the mentoring agent with RAG context."""
    # Search relevant documents in the onboarding index
    search_results = qdrant.search(
        collection_name=collection,
        query_vector=get_embedding(question),
        query_filter={
            "must": [
                {"key": "difficulty",
                 "range": {"lte": junior_profile["current_level"]}}
            ]
        },
        limit=5
    )

    # Build context from retrieved documents
    context_docs = "\n\n---\n\n".join([
        f"[{r.payload['title']}] (Category: {r.payload['category']}, "
        f"Level: {r.payload['difficulty']})\n{r.payload['content']}"
        for r in search_results
    ])

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=MENTOR_SYSTEM_PROMPT.format(
            difficulty_level=junior_profile["current_level"],
            onboarding_week=junior_profile["week"],
            assigned_project_type=junior_profile["project_type"]
        ),
        messages=[{
            "role": "user",
            "content": f"Practice context:\n{context_docs}\n\n"
                       f"Junior's question:\n{question}"
        }]
    )

    return {
        "answer": response.content[0].text,
        "sources": [r.payload["title"] for r in search_results],
        "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
        "gap_detected": "I don't have documentation" in response.content[0].text
    }

# --- Block 3 ---

from dataclasses import dataclass
from typing import Optional

@dataclass
class Scenario:
    """Practice scenario for onboarding."""
    scenario_id: str
    title: str
    difficulty: int                  # 1-5
    category: str                    # "analysis", "delivery", "client", "estimation"
    context: str                     # Situation the junior must resolve
    materials: list[str]             # Attached documents (RFP fragments, etc.)
    task: str                        # What the junior is asked to do
    evaluation_criteria: list[dict]  # Criteria with weights for evaluation
    max_time_minutes: int = 60
    reference_solution: str = ""     # Reference solution (not shown to junior)
    common_mistakes: list[str] = None  # Common mistakes to detect

SCENARIOS_LIBRARY = [
    Scenario(
        scenario_id="SCN-001",
        title="Requirements analysis from a public sector RFP",
        difficulty=1,
        category="analysis",
        context="""A public body has published an RFP for a security audit.
        Your manager asks you to extract the mandatory solvency
        requirements and the evaluation criteria with their
        weightings. You have the relevant RFP fragment.""",
        materials=["simulated_rfp_fragment_01.md"],
        task="""Produce a table with: (1) mandatory solvency requirements,
        (2) evaluation criteria with weightings, (3) key deadlines.
        Include a go/no-go recommendation with justification.""",
        evaluation_criteria=[
            {"criterion": "Completeness of extracted requirements", "weight": 0.3},
            {"criterion": "Correctness of weightings", "weight": 0.2},
            {"criterion": "Identification of critical deadlines", "weight": 0.2},
            {"criterion": "Quality of go/no-go recommendation", "weight": 0.3},
        ],
        max_time_minutes=45,
        common_mistakes=[
            "Confusing mandatory requirements with evaluation criteria",
            "Not detecting implicit deadlines (such as rectification period)",
            "Giving a recommendation without considering the team's actual capacity"
        ]
    ),
    Scenario(
        scenario_id="SCN-005",
        title="Managing a critical finding with the client",
        difficulty=3,
        category="client",
        context="""During a security audit you find that the client's
        system has a critical vulnerability in the authentication
        module. The client's CISO tells you informally that
        'they already know but don't have budget to fix it this year'.
        Your project manager is unavailable until tomorrow.""",
        materials=[],
        task="""Describe: (1) what you do in the next 2 hours,
        (2) how you document it, (3) what you tell the CISO,
        (4) what you tell your manager tomorrow. Justify each decision.""",
        evaluation_criteria=[
            {"criterion": "Correct escalation protocol", "weight": 0.3},
            {"criterion": "Adequate finding documentation", "weight": 0.2},
            {"criterion": "Professional communication with the CISO", "weight": 0.25},
            {"criterion": "Managing own and client risk", "weight": 0.25},
        ],
        max_time_minutes=30,
        common_mistakes=[
            "Waiting until tomorrow without doing anything",
            "Sending a formal email to the CISO without first speaking to their manager",
            "Not documenting the informal conversation as evidence",
            "Minimizing the finding because 'the client already knows'"
        ]
    )
]

# --- Block 4 ---

def evaluate_scenario_response(
    scenario: Scenario,
    junior_response: str,
    junior_id: str
) -> dict:
    """Evaluates the junior's response to a simulated scenario."""
    evaluation_prompt = f"""Evaluate the following response from a junior consultant
to a practice scenario.

SCENARIO: {scenario.context}
TASK: {scenario.task}
REFERENCE SOLUTION: {scenario.reference_solution}
COMMON MISTAKES TO DETECT: {scenario.common_mistakes}

JUNIOR'S RESPONSE:
{junior_response}

Evaluate according to these criteria (each from 0 to 10):
{chr(10).join(f"- {c['criterion']} (weight: {c['weight']})" for c in scenario.evaluation_criteria)}

For each criterion, provide:
1. Numerical score (0-10)
2. Justification for the score in 2-3 sentences
3. One specific improvement tip

At the end, indicate:
- Weighted total score (0-10)
- Rating: "excellent" (>8), "acceptable" (6-8), "insufficient" (<6)
- The 2 strengths of the response
- The 2 priority areas for improvement
- If you detect any common mistake from the list, flag it explicitly
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system="You are a consulting training evaluator. You evaluate rigorously "
               "but with pedagogical intent. You are never condescending. "
               "You highlight the good and the improvable with equal clarity.",
        messages=[{"role": "user", "content": evaluation_prompt}]
    )

    return {
        "scenario_id": scenario.scenario_id,
        "junior_id": junior_id,
        "evaluation": response.content[0].text,
        "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
        "timestamp": datetime.now().isoformat()
    }

# --- Block 5 ---

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

@dataclass
class JuniorProgress:
    """Tracking a junior's progress in the program."""
    junior_id: str
    name: str
    start_date: str
    assigned_project_type: str           # "audit_security", "architecture", "ai_adoption"
    current_phase: str = "immersion"     # "immersion", "simulation", "assisted_production"
    current_week: int = 1

    # Immersion metrics (phase 1)
    docs_read: list[str] = field(default_factory=list)
    mentor_queries: int = 0
    mentor_gaps_triggered: int = 0       # Questions with no answer in RAG
    quiz_scores: list[float] = field(default_factory=list)

    # Simulation metrics (phase 2)
    scenarios_completed: list[dict] = field(default_factory=list)
    avg_scenario_score: float = 0.0
    common_weaknesses: list[str] = field(default_factory=list)

    # Production metrics (phase 3)
    deliverables_produced: int = 0
    deliverables_approved: int = 0
    revision_rounds_avg: float = 0.0     # Average revision rounds per deliverable
    first_billable_date: Optional[str] = None

    def days_to_first_billable(self) -> Optional[int]:
        """Calculates days from start to first billable delivery."""
        if not self.first_billable_date:
            return None
        start = datetime.fromisoformat(self.start_date)
        billable = datetime.fromisoformat(self.first_billable_date)
        return (billable - start).days

    def ready_for_next_phase(self) -> bool:
        """Evaluates whether the junior can advance to the next phase."""
        if self.current_phase == "immersion":
            return (len(self.quiz_scores) >= 1
                    and self.quiz_scores[-1] >= 0.8)
        elif self.current_phase == "simulation":
            acceptable = [s for s in self.scenarios_completed
                         if s.get("rating") in ("excelente", "aceptable")]
            return len(acceptable) >= 3
        return False

def generate_weekly_report(progress: JuniorProgress) -> dict:
    """Generates weekly progress report for the human mentor."""
    report_prompt = f"""Generate a weekly progress report for the mentor
of a junior consultant in an onboarding program.

Junior data:
- Week: {progress.current_week}
- Phase: {progress.current_phase}
- Assigned project: {progress.assigned_project_type}
- Documents read: {len(progress.docs_read)}
- AI mentor queries: {progress.mentor_queries}
- Gaps detected: {progress.mentor_gaps_triggered}
- Latest quiz score: {progress.quiz_scores[-1] if progress.quiz_scores else 'N/A'}
- Scenarios completed: {len(progress.scenarios_completed)}
- Average scenario score: {progress.avg_scenario_score:.1f}
- Recurring weaknesses: {', '.join(progress.common_weaknesses) or 'None detected'}

Generate:
1. Progress summary in 3-4 lines
2. Areas where the junior is progressing well (maximum 3)
3. Areas requiring human mentor attention (maximum 3)
4. Recommendation: ready to advance phase? Yes/No with justification
5. Suggested activities for the next week
"""

    response = client.messages.create(
        model="claude-haiku-4-5",  # Haiku for routine reports, lower cost
        max_tokens=1024,
        system="You are a training program coordinator. "
               "Your reports are concise, factual, and action-oriented.",
        messages=[{"role": "user", "content": report_prompt}]
    )

    return {
        "junior_id": progress.junior_id,
        "week": progress.current_week,
        "report": response.content[0].text,
        "phase_transition_recommended": progress.ready_for_next_phase()
    }

# --- Block 6 ---

def pre_review_deliverable(
    deliverable_text: str,
    deliverable_type: str,  # "gap_analysis", "audit_report", "proposal_section"
    style_guide_chunks: list[str]
) -> dict:
    """Automated pre-review before sending to the senior."""
    review_prompt = f"""Review this {deliverable_type} draft produced by
a junior consultant. Compare against the practice's style standards.

STYLE STANDARDS:
{chr(10).join(style_guide_chunks)}

DRAFT:
{deliverable_text}

Review:
1. Format: does it follow the standard structure for this document type?
2. Completeness: are any mandatory sections missing?
3. Terminology: does it use the practice's standard terms or introduce variants?
4. Data: are there unsupported claims or data without sources?
5. Minimum quality: is it ready for senior review or needs more work?

Generate:
- List of necessary corrections before sending to senior (if any)
- Overall assessment: "ready for review" or "needs more work"
- Estimated quality score (1-10)
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system="You are a quality reviewer of consulting documents. "
               "Your goal is to help the junior improve their draft "
               "BEFORE it reaches the senior. Be specific and constructive.",
        messages=[{"role": "user", "content": review_prompt}]
    )

    return {
        "review": response.content[0].text,
        "ready_for_senior": "ready for review" in response.content[0].text.lower()
    }

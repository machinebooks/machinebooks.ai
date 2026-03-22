# Source: The Consultant and the Machine -- Chapter 2
# Pattern: Project modeling, automation potential, lessons learned
from dataclasses import dataclass, field
from enum import Enum

class Phase(Enum):
    PRESALES = "presales"
    DELIVERY = "delivery"
    KNOWLEDGE = "knowledge_capture"

class AutomationPotential(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

@dataclass
class Activity:
    """Represents an activity within a consulting project."""
    name: str
    phase: Phase
    hours_manual: float          # Estimated hours without AI
    hours_assisted: float        # Estimated hours with AI
    automation_potential: AutomationPotential
    requires_client_interaction: bool
    requires_expert_judgment: bool
    frequency_per_project: int   # Times executed per project
    description: str = ""

@dataclass
class ConsultingProject:
    """Structured model of a consulting project."""
    name: str
    client_sector: str
    frameworks: list[str]        # ISO 27001, ENS, DORA, etc.
    duration_weeks: int
    team_size: int
    activities: list[Activity] = field(default_factory=list)

    @property
    def total_hours_manual(self) -> float:
        return sum(
            a.hours_manual * a.frequency_per_project
            for a in self.activities
        )

    @property
    def total_hours_assisted(self) -> float:
        return sum(
            a.hours_assisted * a.frequency_per_project
            for a in self.activities
        )

    @property
    def reduction_percentage(self) -> float:
        if self.total_hours_manual == 0:
            return 0.0
        return (1 - self.total_hours_assisted / self.total_hours_manual) * 100

# --- Project analysis agent ---

import anthropic
import json

client = anthropic.Anthropic(api_key="<YOUR_API_KEY>")

SYSTEM_PROMPT = """You are a technology consulting operations analyst.
Your job: given a consulting project, decompose its activities
by phase (pre-sales, delivery, knowledge capture) and evaluate
the AI automation potential of each activity.

Evaluation criteria:
- HIGH: repetitive, structured task with low variability between projects.
  Examples: regulation search, matrix generation, draft writing.
- MEDIUM: task with both a structured component and a judgment component.
  Examples: gap analysis (mechanical evaluation is automatable,
  prioritization requires client context).
- LOW: task where value is in human interaction or expert judgment.
  Examples: stakeholder meetings, scope negotiation, strategic recommendations.
- NONE: inherently human task.
  Examples: building trust, reading client political dynamics.

For each activity, estimate manual hours and AI-assisted hours.
Be realistic: AI does not eliminate tasks, it accelerates them.
The consultant always reviews.

Return valid JSON with the activity structure by phase."""

def analyze_project(project_description: str) -> dict:
    """Analyzes a project and generates the automation map."""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Analyze this consulting project and generate
the activity breakdown with automation potential:

{project_description}

Respond ONLY with valid JSON. Expected structure:
{{
  "project_summary": "...",
  "phases": {{
    "presales": [
      {{
        "activity": "name",
        "hours_manual": N,
        "hours_assisted": N,
        "automation_potential": "high|medium|low|none",
        "requires_client_interaction": true|false,
        "requires_expert_judgment": true|false,
        "justification": "why this evaluation"
      }}
    ],
    "delivery": [...],
    "knowledge_capture": [...]
  }},
  "total_hours_manual": N,
  "total_hours_assisted": N,
  "reduction_percentage": N,
  "recommendations": ["...", "..."],
  "warnings": ["activities that should NOT be automated and why"]
}}"""
        }]
    )
    return json.loads(message.content[0].text)

# --- Practical example: triple-framework audit ---

project_input = """
Project: Multi-framework compliance audit
Client: Financial sector entity regulated by ECB
Frameworks: ENS (high level), ISO 27001:2022, DORA
Scope: 14 critical information systems
Planned duration: 6 weeks
Team: 2 senior consultants + 1 junior analyst
Deliverables: Audit report per framework, cross-referenced compliance
matrix, prioritized remediation plan, executive presentation.
Context: The client was audited 18 months ago for ENS and ISO 27001.
Previous reports are available. DORA is the first time.
"""

result = analyze_project(project_input)

# --- Automating knowledge capture ---

import anthropic
from datetime import datetime

client = anthropic.Anthropic(api_key="<YOUR_API_KEY>")

def extract_lessons_learned(
    project_name: str,
    deliverables_summary: str,
    deviations: list[str],
    team_feedback: list[str],
    client_feedback: str
) -> dict:
    """Extracts structured lessons learned at project closure."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system="""You are a continuous improvement analyst in a technology
consulting practice. Your job: extract lessons learned from a completed
project, structure them by category, and generate actionable
recommendations for future projects.

Lesson categories:
- ESTIMATION: deviations in effort, timelines, or scope
- METHODOLOGY: what worked and what didn't in the technical approach
- CLIENT: communication patterns, expectations, friction
- TOOLS: effectiveness of agents, RAG, templates used
- TEAM: coordination, onboarding, workload distribution

Each lesson must include: what happened, why it matters,
what to do differently next time. Maximum 3 sentences per lesson.""",
        messages=[{
            "role": "user",
            "content": f"""Project: {project_name}
Closure date: {datetime.now().strftime('%Y-%m-%d')}

Deliverables summary: {deliverables_summary}

Deviations from plan:
{chr(10).join(f'- {d}' for d in deviations)}

Team feedback:
{chr(10).join(f'- {f}' for f in team_feedback)}

Client feedback: {client_feedback}

Generate lessons learned in JSON:
{{
  "project": "name",
  "lessons": [
    {{
      "category": "ESTIMATION|METHODOLOGY|CLIENT|TOOLS|TEAM",
      "title": "brief title",
      "description": "what happened and why it matters",
      "recommendation": "what to do differently",
      "severity": "high|medium|low"
    }}
  ],
  "metrics": {{
    "planned_hours": N,
    "actual_hours": N,
    "deviation_percentage": N,
    "client_satisfaction": "high|medium|low"
  }}
}}"""
        }]
    )
    return json.loads(message.content[0].text)

# --- Complete pipeline: from opportunity to knowledge ---

from dataclasses import dataclass
from enum import Enum

class ProjectStage(Enum):
    OPPORTUNITY = "opportunity"
    PROPOSAL = "proposal"
    DELIVERY = "delivery"
    CLOSURE = "closure"
    KNOWLEDGE = "knowledge_captured"

@dataclass
class ProjectPipeline:
    """Orchestrates the complete flow of a consulting project."""
    project_id: str
    stage: ProjectStage
    analysis: dict = None       # Analysis agent result
    proposal: dict = None       # Generated proposal
    delivery_log: list = None   # Delivery record
    lessons: dict = None        # Lessons learned

    def advance_to_proposal(self, rfp_text: str):
        """Analyzes the opportunity and prepares the analysis for the proposal."""
        self.analysis = analyze_project(rfp_text)
        self.stage = ProjectStage.PROPOSAL
        # The analysis feeds the effort estimation
        # and the technical proposal generation
        return self.analysis

    def advance_to_delivery(self):
        """Transitions to delivery with the automation plan."""
        self.stage = ProjectStage.DELIVERY
        self.delivery_log = []
        # Activities identified as automatable
        # are assigned to agents; human ones to consultants

    def close_and_capture(self, feedback: dict):
        """Closes the project and captures knowledge."""
        self.lessons = extract_lessons_learned(
            project_name=self.project_id,
            deliverables_summary=feedback.get("deliverables", ""),
            deviations=feedback.get("deviations", []),
            team_feedback=feedback.get("team", []),
            client_feedback=feedback.get("client", "")
        )
        self.stage = ProjectStage.KNOWLEDGE
        # Lessons are indexed for RAG
        # and feed future project estimations
        return self.lessons

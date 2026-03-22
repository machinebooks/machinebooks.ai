# Source: The Consultant and the Machine -- Chapter 12
# Pattern: Automated audit agent: triage, evaluation, findings, MCP
import anthropic
import json
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class AuditControl:
    """Represents a control from the reference framework."""
    control_id: str
    title: str
    description: str
    category: str
    # Evaluation result
    status: str = "pending"  # complies | non_compliant | partial | not_applicable
    evidence_refs: list[str] = field(default_factory=list)
    justification: str = ""
    finding: dict | None = None

@dataclass
class AuditFinding:
    """Structured audit finding."""
    finding_id: str
    control_id: str
    severity: str  # high | medium | low | observation
    title: str
    description: str
    evidence_quote: str  # Verifiable verbatim quote
    risk: str
    recommendation: str
    compensating_controls: str = ""

class AuditAgent:
    """Audit agent that evaluates controls against evidence."""

    def __init__(self, framework: str, model: str = "claude-sonnet-4-6"):
        self.client = anthropic.Anthropic()
        self.model = model
        self.framework = framework
        self.controls: list[AuditControl] = []
        self.findings: list[AuditFinding] = []
        self.documents: dict[str, str] = {}  # name -> content

    def load_framework(self, controls_path: str):
        """Loads reference framework controls."""
        with open(controls_path, "r") as f:
            raw_controls = json.load(f)
        self.controls = [
            AuditControl(**ctrl) for ctrl in raw_controls
        ]
        print(f"Loaded {len(self.controls)} controls from {self.framework}")

# --- Block 2 ---

    def triage_document(self, doc_name: str, doc_content: str) -> dict:
        """Classifies a document by relevance and domain."""
        # Use claude-haiku-4-5 for triage: fast and economical
        response = self.client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": f"""Classify this document for a {self.framework} audit.

Document: {doc_name}
Content (first 2,000 words): {doc_content[:8000]}

Respond ONLY in JSON:
{{
  "relevant": true/false,
  "domain": "security|compliance|processes|architecture|other",
  "controls_related": ["list of potentially related control IDs"],
  "summary": "one-sentence summary"
}}"""
            }]
        )
        return json.loads(response.content[0].text)

# --- Block 3 ---

    def evaluate_control(self, control: AuditControl) -> AuditControl:
        """Evaluates a control against available evidence."""
        relevant_docs = self._find_relevant_docs(control)

        if not relevant_docs:
            control.status = "no_cumple"
            control.justification = (
                "No documentation found evidencing "
                f"implementation of {control.title}."
            )
            return control

        evidence_context = "\n\n---\n\n".join([
            f"**Document: {name}**\n{content[:4000]}"
            for name, content in relevant_docs.items()
        ])

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=f"""You are an expert auditor in {self.framework}.
Evaluate whether the presented evidence demonstrates compliance
with the indicated control.

Rules:
- If evidence demonstrates full compliance: "cumple"
- If evidence is partial or outdated: "parcial"
- If there's insufficient evidence: "no_cumple"
- If the control doesn't apply to the context: "no_aplica"
- ALWAYS include a verbatim quote from relevant evidence
- ALWAYS justify your evaluation with facts from the document
- NEVER invent evidence that isn't in the documents""",
            messages=[{
                "role": "user",
                "content": f"""Control: {control.control_id} — {control.title}
Description: {control.description}

Available evidence:
{evidence_context}

Respond in JSON:
{{
  "status": "cumple|parcial|no_cumple|no_aplica",
  "justification": "detailed explanation",
  "evidence_quotes": ["verbatim document quotes"],
  "gaps_identified": ["detected gaps"],
  "risk_if_not_addressed": "risk if not remediated"
}}"""
            }]
        )

        result = json.loads(response.content[0].text)
        control.status = result["status"]
        control.justification = result["justification"]
        control.evidence_refs = [name for name in relevant_docs.keys()]
        return control

# --- Audit configuration (YAML) ---
# The following YAML configuration defines the multi-framework
# audit setup referenced in the code above.
#
# # audit_config.yaml — Multi-framework audit configuration
# frameworks:
#   iso27001:
#     name: "ISO/IEC 27001:2022"
#     controls_file: "frameworks/iso27001_annexA.json"
#     system_context: >
#       Certified ISO 27001 Lead Auditor. Evaluates Annex A
#       controls according to the 2022 version.
# 
#   ens:
#     name: "Esquema Nacional de Seguridad (ENS)"
#     controls_file: "frameworks/ens_controles.json"
#     system_context: >
#       ENS auditor with knowledge of security measures
#       from RD 311/2022.
# 
#   dora:
#     name: "Digital Operational Resilience Act (DORA)"
#     controls_file: "frameworks/dora_requirements.json"
#     system_context: >
#       DORA specialist auditor. Evaluates the five pillars:
#       ICT risk management, incident reporting, resilience
#       testing, ICT third-party management, and information sharing.
# 
# audit_settings:
#   triage_model: "claude-haiku-4-5"
#   evaluation_model: "claude-sonnet-4-6"
#   finding_model: "claude-sonnet-4-6"
#   human_review_required: true  # NEVER disable

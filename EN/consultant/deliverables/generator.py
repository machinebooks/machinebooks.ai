# Source: The Consultant and the Machine -- Chapter 6
# Pattern: Three-phase deliverable pipeline with quality gates
import anthropic
import yaml
from pathlib import Path
from dataclasses import dataclass

@dataclass
class GenerationResult:
    section_id: str
    content: str
    tokens_used: int
    model: str
    template_version: str

class DeliverableGenerator:
    """Three-phase deliverable generation pipeline."""

    def __init__(self, template_path: str):
        self.client = anthropic.Anthropic()
        self.template = self._load_template(template_path)
        self.model = "claude-sonnet-4-6"
        self.results: list[GenerationResult] = []

    def _load_template(self, path: str) -> dict:
        with open(path) as f:
            return yaml.safe_load(f)["template"]

    def _build_system_prompt(self, section: dict) -> str:
        """Builds system prompt combining voice + section."""
        voice = self.template["voice"]
        return f"""You are a senior consultant writing a
{self.template['document_type']} report under the
{self.template['framework']} framework.

TONE AND STYLE:
- Formality: {voice['formality']}
- Assertiveness: {voice['assertiveness']}
- Grammatical person: {voice['person']}
- Prohibited terms: {', '.join(voice['prohibited_terms'])}

SECTION INSTRUCTIONS:
{section['instructions']}

Maximum words: {section.get('max_words', 'no limit')}
"""

    def generate_section(
        self, section: dict, data: dict, outline: str
    ) -> GenerationResult:
        """Generates an individual section with global context."""
        system = self._build_system_prompt(section)
        user_content = f"""GLOBAL DOCUMENT OUTLINE:
{outline}

DATA FOR THIS SECTION:
{self._format_data(section, data)}

Generate the '{section['id']}' section of the report."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": user_content}]
        )
        content = response.content[0].text
        return GenerationResult(
            section_id=section["id"],
            content=content,
            tokens_used=response.usage.input_tokens
                + response.usage.output_tokens,
            model=self.model,
            template_version=self.template["version"],
        )

# --- Block 2 ---

    def generate_full_report(self, assessment_data: dict) -> str:
        """Complete three-phase pipeline."""
        # Phase 1: Global outline
        outline = self._generate_outline(assessment_data)

        # Phase 2: Section-by-section generation
        sections_content = {}
        total_tokens = 0
        for section in self.template["sections"]:
            if section.get("static_content"):
                sections_content[section["id"]] = (
                    self._get_static_content(section["id"])
                )
                continue
            result = self.generate_section(
                section, assessment_data, outline
            )
            sections_content[section["id"]] = result.content
            total_tokens += result.tokens_used
            self.results.append(result)

        # Phase 3: Coherence review
        assembled = self._assemble_document(sections_content)
        coherent = self._review_coherence(assembled)

        # Record generation metadata
        self._save_metadata(assessment_data, total_tokens)
        return coherent

    def _generate_outline(self, data: dict) -> str:
        """Phase 1: outline with main findings."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": f"""From this assessment data,
generate a report outline with:
1. The 5 most critical findings
2. The overall compliance percentage
3. The general tone (alarming/concerning/acceptable)
4. The 3 priority recommendations

Data: {self._summarize_data(data)}"""
            }]
        )
        return response.content[0].text

# --- Block 3 ---

class ComplianceMatrixGenerator:
    """Generates compliance matrices control by control."""

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-6"

    def generate_control_assessment(
        self, control: dict, evidence: dict, context: str
    ) -> dict:
        """Evaluates an individual control against the evidence."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system="""You are an auditor evaluating a security
control. Respond ONLY in JSON with this structure:
{
  "control_id": "...",
  "status": "compliant|partially_compliant|non_compliant",
  "evidence_summary": "...",
  "gap_description": "..." or null,
  "risk_level": "high|medium|low",
  "remediation": "...",
  "effort_hours": N,
  "priority": "quick_win|medium_term|long_term"
}
Be direct. Do not use hedging. If non-compliant, say non-compliant.""",
            messages=[{
                "role": "user",
                "content": f"""CONTROL:
ID: {control['id']}
Title: {control['title']}
Description: {control['description']}
Compliance criteria: {control['criteria']}

CLIENT EVIDENCE:
{evidence.get('description', 'No evidence provided')}

ASSESSMENT CONTEXT:
{context}

Evaluate this control."""
            }]
        )
        # Parse JSON response
        import json
        return json.loads(response.content[0].text)

    def generate_matrix(
        self, controls: list[dict], evidences: dict, context: str
    ) -> list[dict]:
        """Generates the complete matrix, control by control."""
        results = []
        for control in controls:
            evidence = evidences.get(control["id"], {})
            assessment = self.generate_control_assessment(
                control, evidence, context
            )
            results.append(assessment)
        return results

# --- Block 4 ---

from enum import Enum
from datetime import datetime

class ReviewStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    NEEDS_REVISION = "needs_revision"
    REJECTED = "rejected"

class QualityChecker:
    """Quality control with mandatory human review."""

    def __init__(self, template: dict):
        self.template = template
        self.reviews: dict[str, ReviewStatus] = {}
        self.automated_checks: list[dict] = []

    def run_automated_checks(self, document: str) -> list[dict]:
        """Automated verifications before human review."""
        issues = []

        # Verify minimum length per section
        for section in self.template["sections"]:
            max_words = section.get("max_words")
            if max_words:
                actual = self._count_words_in_section(
                    document, section["id"]
                )
                if actual < max_words * 0.7:
                    issues.append({
                        "section": section["id"],
                        "type": "underfilled",
                        "detail": f"{actual} words vs "
                                  f"{max_words} target",
                        "severity": "warning"
                    })

        # Verify no unresolved placeholders
        placeholders = ["[COMPLETE]", "[TODO]", "[VERIFY]",
                        "<<PENDING>>"]
        for ph in placeholders:
            if ph in document:
                issues.append({
                    "section": "global",
                    "type": "unresolved_placeholder",
                    "detail": f"Placeholder '{ph}' found",
                    "severity": "blocker"
                })

        # Verify numeric data consistency
        issues.extend(self._check_numeric_consistency(document))

        # Verify prohibited terms
        voice = self.template["voice"]
        for term in voice.get("prohibited_terms", []):
            if term.lower() in document.lower():
                issues.append({
                    "section": "global",
                    "type": "prohibited_term",
                    "detail": f"Prohibited term: '{term}'",
                    "severity": "warning"
                })

        self.automated_checks = issues
        return issues

    def get_review_requirements(self) -> list[dict]:
        """Lists sections requiring human review."""
        requirements = []
        for section in self.template["sections"]:
            if section.get("requires_human_review", False):
                requirements.append({
                    "section": section["id"],
                    "status": self.reviews.get(
                        section["id"], ReviewStatus.PENDING
                    ),
                    "reviewer_required": "senior",
                })
        return requirements

    def is_deliverable_ready(self) -> tuple[bool, list[str]]:
        """Verifies whether the document can be delivered."""
        blockers = []

        # Verify automated checks
        for issue in self.automated_checks:
            if issue["severity"] == "blocker":
                blockers.append(
                    f"Blocker: {issue['detail']} "
                    f"in {issue['section']}"
                )

        # Verify human reviews
        for section in self.template["sections"]:
            if section.get("requires_human_review"):
                status = self.reviews.get(section["id"])
                if status != ReviewStatus.APPROVED:
                    blockers.append(
                        f"Review pending: {section['id']} "
                        f"({status or 'not reviewed'})"
                    )

        return (len(blockers) == 0, blockers)

# --- Block 5 ---

def enrich_with_rag_context(
    self, section_id: str, query: str, filters: dict
) -> str:
    """Searches for relevant context in the knowledge base."""
    # Query Qdrant with type and sector filters
    results = self.rag_client.search(
        query=query,
        filters={
            "document_type": ["report", "lesson_learned"],
            "sector": filters.get("sector", None),
            "framework": filters.get("framework", None),
        },
        top_k=5,
    )

    if not results:
        return ""

    # Format context for injection
    context_parts = []
    for r in results:
        context_parts.append(
            f"[Source: {r.metadata['document_type']}, "
            f"{r.metadata['year']}]\n{r.text}"
        )
    return "\n---\n".join(context_parts)

# --- Block 6 ---

import subprocess

def export_to_docx(
    markdown_path: str,
    output_path: str,
    reference_doc: str = "templates/practice-template.docx"
) -> None:
    """Converts Markdown to Word with practice styling."""
    cmd = [
        "pandoc", markdown_path,
        "-o", output_path,
        "--reference-doc", reference_doc,
        "--toc",                   # Table of contents
        "--toc-depth=3",
        "--metadata", "lang=en-US",
        "--lua-filter", "filters/table-numbering.lua",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Pandoc error: {result.stderr}"
        )

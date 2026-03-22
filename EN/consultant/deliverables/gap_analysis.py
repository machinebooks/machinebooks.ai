# Source: The Consultant and the Machine -- Chapter 13
# Pattern: Multi-framework gap analysis with deduplication
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional

class MaturityLevel(IntEnum):
    """Maturity levels for control evaluation."""
    INEXISTENTE = 0   # No evidence of implementation
    INICIAL = 1       # Exists ad-hoc, not formalized
    DEFINIDO = 2      # Documented and formally approved
    GESTIONADO = 3    # Implemented, measured, and reviewed
    OPTIMIZADO = 4    # Continuous improvement with metrics

@dataclass
class Control:
    """A control within a regulatory framework."""
    framework: str          # "ISO27001", "ENS", "NIS2", "AI_ACT"
    control_id: str         # "A.8.1", "org.1", "Art.21.2.a"
    title: str
    description: str
    category: str           # Thematic grouping
    cross_references: list[str] = field(default_factory=list)

@dataclass
class GapFinding:
    """Result of evaluating a control against evidence."""
    control: Control
    current_level: MaturityLevel
    target_level: MaturityLevel
    evidence_summary: str
    gap_description: str
    remediation: str
    effort_days: float
    priority: str           # "critical", "high", "medium", "low"
    confidence: float       # 0.0-1.0
    affected_frameworks: list[str] = field(default_factory=list)

# --- Block 2 ---

import anthropic
import yaml
from pathlib import Path

class GapAnalysisAgent:
    """Multi-framework gap analysis agent."""

    def __init__(self, org_profile: str, target_level: MaturityLevel):
        self.client = anthropic.Anthropic()
        self.org_profile = org_profile
        self.target_level = target_level
        self.frameworks: dict[str, list[Control]] = {}
        self.criteria: dict[str, EvaluationCriteria] = {}
        self.findings: list[GapFinding] = []

    def evaluate_control(
        self, control: Control, evidence_text: str
    ) -> GapFinding:
        """Evaluates a control against client evidence."""
        criteria = self.criteria.get(
            f"{control.control_id}:{self.org_profile}"
        )
        criteria_text = self._format_criteria(criteria)

        prompt = f"""Evaluate the following regulatory control against
client evidence.

CONTROL: {control.framework} {control.control_id}
— {control.title}
Description: {control.description}

ORGANIZATION PROFILE: {self.org_profile}

EVALUATION CRITERIA BY LEVEL:
{criteria_text}

CLIENT EVIDENCE:
{evidence_text}

Respond in JSON with these fields:
- current_level: current level (0-4)
- gap_description: what's missing to reach level {self.target_level.value}
- remediation: concrete recommended actions
- effort_days: effort estimate in person-days
- priority: "critical", "high", "medium", or "low"
- confidence: evaluation confidence (0.0-1.0)
- reasoning: step-by-step evaluation reasoning"""

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system="""You are an expert auditor in security and
compliance regulations. You evaluate controls rigorously
but fairly. If evidence is insufficient to evaluate,
indicate low confidence. Never assume compliance without
evidence. Never exaggerate gaps without justification.""",
            messages=[{"role": "user", "content": prompt}],
        )
        return self._parse_finding(control, response)

# --- Block 3 ---

class MultiFrameworkAnalyzer:
    """Analyzes gaps crossing multiple frameworks."""

    def _group_by_cross_reference(
        self, findings: list[GapFinding]
    ) -> list[list[GapFinding]]:
        """Groups findings that refer to the same real gap."""
        # Union-Find to group equivalent controls
        parent: dict[str, str] = {}

        def find(x: str) -> str:
            while parent.get(x, x) != x:
                x = parent[x]
            return x

        def union(a: str, b: str) -> None:
            parent[find(a)] = find(b)

        # Build groups based on cross_references
        for finding in findings:
            ctrl = finding.control
            key = f"{ctrl.framework}:{ctrl.control_id}"
            for ref in ctrl.cross_references:
                union(key, ref)

        # Group findings by root
        groups_map: dict[str, list[GapFinding]] = {}
        for finding in findings:
            ctrl = finding.control
            key = f"{ctrl.framework}:{ctrl.control_id}"
            root = find(key)
            groups_map.setdefault(root, []).append(finding)

        return list(groups_map.values())

# --- Block 4 ---

def generate_executive_summary(
    gaps: list[GapFinding],
    roadmap: list[RemediationAction],
    org_profile: str,
) -> str:
    """Generates executive summary with Claude Opus."""
    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        system="""You are a senior security and compliance
consultant with 20 years of experience. Write an executive
summary for the organization's management. Tone: direct,
without alarmism but without minimizing.""",
        messages=[{"role": "user", "content": f"""
Organization profile: {org_profile}

GAP SUMMARY:
{_format_gap_summary(gaps)}

PROPOSED REMEDIATION ROADMAP:
{_format_roadmap_summary(roadmap)}

Generate an executive summary including:
1. Overall compliance position (% per framework)
2. The 5 most relevant risks and their potential impact
3. Total estimated investment (person-days and timeline)
4. Strategic recommendation: where to start and why
5. What happens if no action is taken (cost of inaction)"""}],
    )
    return response.content[0].text

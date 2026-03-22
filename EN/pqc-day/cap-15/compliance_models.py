"""
PQC-Day and the Machine — Chapter 15
Pattern: Compliance models — Framework, Control, Assessment for NIS2/DORA

This is a didactic example from the book, not production code.
See chapter 15 for full context and explanation.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional, Dict
import json


@dataclass
class ComplianceFramework:
    """Regulatory framework: NIS2, DORA, ISO 27001, NIST CSF 2.0..."""
    id: int = 0
    code: str = ""              # 'NIS2'
    name: str = ""              # 'NIS2 Directive (EU) 2022/2555'
    description: str = ""
    version: str = ""           # '2022/2555'
    category: str = "Security"
    is_active: bool = True
    total_controls: int = 0


@dataclass
class ComplianceControl:
    """Individual control within a regulatory framework."""
    id: int = 0
    framework_id: int = 0
    reference: str = ""         # 'NIS2.RISK.8'
    title: str = ""
    description: str = ""
    guidance: str = ""
    parent_control_id: Optional[int] = None
    category: str = ""          # 'Technical', 'Organizational'
    domain: str = ""            # 'Risk Management'
    is_mandatory: bool = True
    sequence_order: int = 0
    keywords: str = ""          # JSON: ["cryptography", "encryption", "PQC"]
    pqc_relevant: bool = False
    cloud_relevant: bool = False


@dataclass
class ComplianceAssessment:
    """Compliance evaluation: a client against a framework."""
    id: int = 0
    client_id: int = 0
    framework_id: int = 0
    name: str = ""
    assessment_date: date = field(default_factory=date.today)
    assessor: str = ""
    status: str = "draft"       # draft, in_progress, completed, approved
    overall_score: float = 0.0

    # Compliance statistics
    total_controls: int = 0
    implemented_controls: int = 0
    partial_controls: int = 0
    not_implemented_controls: int = 0
    not_applicable_controls: int = 0


@dataclass
class ControlAssessment:
    """Assessment of a specific control within an assessment."""
    id: int = 0
    assessment_id: int = 0
    control_id: int = 0

    # Human evaluation
    implementation_status: str = "not_assessed"  # not_assessed, not_implemented,
                                                 # partial, implemented, not_applicable
    effectiveness_level: str = "none"            # none, low, medium, high

    # Evidence and findings
    evidence_description: str = ""
    findings: str = ""
    recommendations: str = ""
    gaps: str = ""

    # Source of evaluation
    source: str = "manual"      # manual, code_analysis, cloud_analysis, ai_suggestion
    source_finding_ids: str = "[]"  # JSON array

    # AI suggestions — the auditor decides whether to accept
    ai_suggested_status: str = ""
    ai_confidence: float = 0.0
    ai_reasoning: str = ""


@dataclass
class FindingControlMapping:
    """Auditable record of finding -> control mapping."""
    id: int = 0
    finding_type: str = ""      # 'crypto', 'vulnerability'
    finding_id: int = 0
    control_id: int = 0
    mapping_type: str = "violation"  # violation, partial, recommendation
    confidence: float = 0.0
    notes: str = ""
    is_auto_mapped: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


# --- Sample NIS2 controls ---

def create_nis2_framework() -> tuple:
    """Create a sample NIS2 framework with controls."""
    framework = ComplianceFramework(
        id=1, code='NIS2',
        name='NIS2 Directive (EU) 2022/2555',
        version='2022/2555',
        category='Security'
    )

    controls = [
        ComplianceControl(
            id=1, framework_id=1, reference='NIS2.RISK.1',
            title='Risk Management Policy',
            domain='Risk Management', category='Organizational',
            pqc_relevant=True,
            keywords='["risk", "policy", "assessment"]'
        ),
        ComplianceControl(
            id=2, framework_id=1, reference='NIS2.RISK.4',
            title='Supply Chain Security',
            domain='Supply Chain', category='Technical',
            pqc_relevant=True,
            keywords='["supply-chain", "third-party", "dependency", "vendor"]'
        ),
        ComplianceControl(
            id=8, framework_id=1, reference='NIS2.RISK.8',
            title='Cryptography and Encryption Policies',
            domain='Cryptography', category='Technical',
            pqc_relevant=True,
            keywords='["cryptography", "encryption", "rsa", "aes", "certificate", '
                     '"tls", "pqc", "quantum"]'
        ),
        ComplianceControl(
            id=9, framework_id=1, reference='NIS2.RISK.9',
            title='Access Control and Authentication',
            domain='Access Control', category='Technical',
            pqc_relevant=False,
            keywords='["access", "authentication", "mfa", "password", "credential"]'
        ),
        ComplianceControl(
            id=10, framework_id=1, reference='NIS2.RISK.10',
            title='Multi-Factor Authentication',
            domain='Access Control', category='Technical',
            pqc_relevant=False,
            keywords='["mfa", "two-factor", "authentication"]'
        ),
    ]

    framework.total_controls = len(controls)
    return framework, controls


# --- Main ---
if __name__ == '__main__':
    framework, controls = create_nis2_framework()

    print(f"Framework: {framework.name}")
    print(f"Total controls: {framework.total_controls}\n")

    for c in controls:
        pqc = " [PQC]" if c.pqc_relevant else ""
        print(f"  {c.reference:15s} {c.title}{pqc}")
        print(f"    Domain: {c.domain}, Category: {c.category}")

    # Sample assessment
    assessment = ComplianceAssessment(
        id=1, client_id=1, framework_id=1,
        name="Q1 2025 NIS2 Assessment",
        total_controls=len(controls),
        implemented_controls=1,
        partial_controls=2,
        not_implemented_controls=2
    )

    score = ((assessment.implemented_controls * 100 +
              assessment.partial_controls * 50) /
             max(assessment.total_controls, 1))

    print(f"\nAssessment: {assessment.name}")
    print(f"Score: {score:.1f}%")
    print(f"  Implemented: {assessment.implemented_controls}")
    print(f"  Partial: {assessment.partial_controls}")
    print(f"  Not implemented: {assessment.not_implemented_controls}")

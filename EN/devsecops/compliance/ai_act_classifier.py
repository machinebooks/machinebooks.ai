# Source: The DevSecOps and the Machine -- Chapter 17
# Pattern: AI Act risk classification and conformity assessment

import anthropic
import yaml
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    UNACCEPTABLE = "unacceptable"
    HIGH = "high"
    LIMITED = "limited"
    MINIMAL = "minimal"

@dataclass
class ClassificationResult:
    risk_level: RiskLevel
    confidence: float          # 0.0 to 1.0
    rationale: str
    applicable_articles: list  # Applicable AI Act articles
    obligations: list          # Derived obligations
    requires_human_review: bool

# Annex III domains that imply high risk
ANNEX_III_DOMAINS = {
    "biometric_identification": RiskLevel.HIGH,
    "critical_infrastructure": RiskLevel.HIGH,
    "education_training": RiskLevel.HIGH,
    "employment_hr": RiskLevel.HIGH,
    "essential_services": RiskLevel.HIGH,
    "law_enforcement": RiskLevel.HIGH,
    "migration_asylum": RiskLevel.HIGH,
    "justice_democracy": RiskLevel.HIGH,
}

# Prohibited practices under Art. 5
PROHIBITED_PRACTICES = [
    "social_scoring",
    "subliminal_manipulation",
    "exploitation_vulnerable",
    "real_time_biometric_public",
    "emotion_recognition_workplace",
    "untargeted_facial_scraping",
]

def classify_deterministic(manifest: dict) -> ClassificationResult | None:
    """Deterministic classification by fixed rules — covers clear-cut cases."""
    purpose = manifest.get("purpose", {})
    domain = purpose.get("domain", "")
    use_case = purpose.get("use_case", "")

    # Check prohibited practices
    for practice in PROHIBITED_PRACTICES:
        if practice in use_case.lower() or practice in domain.lower():
            return ClassificationResult(
                risk_level=RiskLevel.UNACCEPTABLE,
                confidence=0.95,
                rationale=f"Use case matches prohibited practice: {practice}",
                applicable_articles=["Art. 5"],
                obligations=["Total prohibition — do not deploy"],
                requires_human_review=True
            )

    # Check Annex III domains
    if domain in ANNEX_III_DOMAINS:
        return ClassificationResult(
            risk_level=ANNEX_III_DOMAINS[domain],
            confidence=0.90,
            rationale=f"Domain '{domain}' listed in AI Act Annex III",
            applicable_articles=["Art. 6", "Art. 9-15", "Art. 43"],
            obligations=_high_risk_obligations(),
            requires_human_review=False
        )

    # If no deterministic match, return None for LLM evaluation
    return None

def classify_with_agent(manifest: dict) -> ClassificationResult:
    """Classification with Claude for cases requiring interpretation."""
    client = anthropic.Anthropic()

    prompt = f"""Analyze the following AI system and classify it according to
Regulation (EU) 2024/1689 (AI Act).

SYSTEM MANIFEST:
{yaml.dump(manifest, default_flow_style=False)}

CLASSIFICATION CRITERIA:
- UNACCEPTABLE (Art. 5): social scoring, subliminal manipulation,
  exploitation of vulnerabilities of specific groups, real-time
  remote biometric identification in public spaces.
- HIGH RISK (Annex III): systems in biometrics, critical
  infrastructure, education, employment, essential services, justice,
  migration, democratic processes.
- LIMITED (Art. 50): chatbots, deepfakes, content generation
  systems requiring transparency about AI nature.
- MINIMAL: all others.

RESPOND in JSON with this exact structure:
{{
  "risk_level": "unacceptable|high|limited|minimal",
  "confidence": 0.0-1.0,
  "rationale": "explanation in 2-3 sentences",
  "applicable_articles": ["Art. X", ...],
  "obligations": ["obligation 1", ...],
  "requires_human_review": true/false
}}

If confidence is below 0.7, set requires_human_review to true."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse JSON response and build ClassificationResult
    import json
    result_data = json.loads(response.content[0].text)
    return ClassificationResult(
        risk_level=RiskLevel(result_data["risk_level"]),
        confidence=result_data["confidence"],
        rationale=result_data["rationale"],
        applicable_articles=result_data["applicable_articles"],
        obligations=result_data["obligations"],
        requires_human_review=result_data["requires_human_review"]
    )

from dataclasses import dataclass, field

@dataclass
class ComplianceCheck:
    article: str
    requirement: str
    check_type: str        # "automated" | "agent" | "manual"
    status: str = "pending"  # "passed" | "failed" | "warning" | "pending"
    evidence: str = ""
    details: str = ""

def build_high_risk_checklist(pipeline_artifacts: dict) -> list[ComplianceCheck]:
    """Generate checklist for high-risk system based on pipeline artifacts."""
    checks = []

    # Art. 9 — Risk management system
    checks.append(ComplianceCheck(
        article="Art. 9",
        requirement="Documentation of identified risks and mitigation measures",
        check_type="agent",
        status="passed" if pipeline_artifacts.get("risk_assessment") else "failed",
        evidence=pipeline_artifacts.get("risk_assessment_path", "")
    ))

    # Art. 10 — Data and data governance
    checks.append(ComplianceCheck(
        article="Art. 10",
        requirement="Documentation of training/validation/test data",
        check_type="automated",
        status="passed" if pipeline_artifacts.get("data_card") else "failed",
        evidence=pipeline_artifacts.get("data_card_path", "")
    ))

    # Art. 11 — Technical documentation
    checks.append(ComplianceCheck(
        article="Art. 11",
        requirement="Complete technical documentation per Annex IV",
        check_type="agent",
        status="passed" if pipeline_artifacts.get("technical_doc") else "failed",
        evidence=pipeline_artifacts.get("technical_doc_path", "")
    ))

    # Art. 12 — Event logging
    has_logging = pipeline_artifacts.get("llm_usage_logs", False)
    checks.append(ComplianceCheck(
        article="Art. 12",
        requirement="Automatic logging of AI system operations",
        check_type="automated",
        status="passed" if has_logging else "failed",
        evidence="LLM usage logs active" if has_logging else "No logging detected"
    ))

    # Art. 13 — Transparency
    checks.append(ComplianceCheck(
        article="Art. 13",
        requirement="Usage instructions for deployers with sufficient information",
        check_type="agent",
        status="pending",  # Requires qualitative evaluation
        evidence=pipeline_artifacts.get("user_instructions_path", "")
    ))

    # Art. 14 — Human oversight
    autonomy = pipeline_artifacts.get("autonomy_level", "autonomous")
    checks.append(ComplianceCheck(
        article="Art. 14",
        requirement="Human oversight mechanism implemented",
        check_type="automated",
        status="passed" if autonomy != "autonomous" else "failed",
        evidence=f"Autonomy level: {autonomy}"
    ))

    # Art. 15 — Accuracy, robustness, and cybersecurity
    has_security_scan = pipeline_artifacts.get("sast_results") is not None
    has_sca = pipeline_artifacts.get("sbom") is not None
    checks.append(ComplianceCheck(
        article="Art. 15 (ciberseguridad)",
        requirement="Security scanning of code and dependencies",
        check_type="automated",
        status="passed" if (has_security_scan and has_sca) else "failed",
        evidence=f"SAST: {'yes' if has_security_scan else 'no'}, SCA/SBOM: {'yes' if has_sca else 'no'}"
    ))

    # Art. 15 — Adversarial resilience
    has_prompt_injection_test = pipeline_artifacts.get("prompt_injection_results")
    checks.append(ComplianceCheck(
        article="Art. 15 (resiliencia)",
        requirement="Testing adversarial contra prompt injection",
        check_type="automated",
        status="passed" if has_prompt_injection_test else "warning",
        evidence=pipeline_artifacts.get("prompt_injection_summary", "No adversarial tests")
    ))

    return checks

import anthropic
from datetime import datetime

def generate_technical_documentation(
    manifest: dict,
    classification: dict,
    pipeline_artifacts: dict,
    compliance_checks: list[dict]
) -> str:
    """Generate technical documentation per AI Act Annex IV."""
    client = anthropic.Anthropic()

    # Build context with all available artifacts
    context = f"""
SYSTEM: {manifest['system']['name']} v{manifest['system']['version']}
CLASSIFICATION: {classification['risk_level']} (confidence: {classification['confidence']})
DATE: {datetime.now().isoformat()}

AI COMPONENTS:
{yaml.dump(manifest.get('ai_components', {}), default_flow_style=False)}

AVAILABLE SECURITY ARTIFACTS:
- SBOM: {'yes' if pipeline_artifacts.get('sbom') else 'no'}
- SAST results: {pipeline_artifacts.get('sast_summary', 'not available')}
- SCA results: {pipeline_artifacts.get('sca_summary', 'not available')}
- Prompt injection tests: {pipeline_artifacts.get('prompt_injection_summary', 'not available')}
- LLM usage logs: {'configured' if pipeline_artifacts.get('llm_usage_logs') else 'not configured'}

COMPLIANCE CHECKS:
{_format_checks(compliance_checks)}
"""

    prompt = f"""Generate the technical documentation for the following AI system
per Annex IV of Regulation (EU) 2024/1689 (AI Act).

{context}

The documentation MUST contain these sections (Annex IV):
1. General description of the AI system
2. Detailed description of elements and development process
3. Information on monitoring, functioning, and control
4. Description of the risk management system (Art. 9)
5. Description of changes made during the lifecycle
6. List of applied harmonized standards
7. Copy of the EU declaration of conformity (if available)
8. Description of the post-market performance evaluation system

For each section:
- If data is available in the artifacts, use it with concrete references
- If data is missing, mark the section as "[PENDING - requires manual input]"
- Do not invent data or metrics not present in the provided context

Format: Markdown with numbered sections."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text
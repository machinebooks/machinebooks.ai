# Extracted from: LibroAISafety/ch-10-operational-governance.md
# ai_policy_engine.py — Policy engine for AI systems
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable

class PolicyResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"

@dataclass
class PolicyRule:
    """An automatically verifiable policy rule."""
    rule_id: str
    description: str
    severity: str          # "blocking", "warning"
    check: Callable        # Function that evaluates the rule
    remediation: str       # What to do if not compliant

@dataclass
class PolicyEvaluation:
    """Result of evaluating all policies for a system."""
    system_name: str
    timestamp: datetime
    results: list[dict]
    deployable: bool       # True if no blocking rules in FAIL

def create_ai_policy_rules() -> list[PolicyRule]:
    """
    Defines policy rules as code.
    Each rule is a function that evaluates a system.
    """
    rules = [
        PolicyRule(
            rule_id="POL-001",
            description="System must have assigned risk classification",
            severity="blocking",
            check=lambda s: PolicyResult.PASS 
                if s.get("risk_tier") 
                else PolicyResult.FAIL,
            remediation="Run classify_ai_act_risk() and assign tier"
        ),
        PolicyRule(
            rule_id="POL-002",
            description="Current security evaluation per tier",
            severity="blocking",
            check=lambda s: _check_eval_currency(s),
            remediation="Run updated security evaluation"
        ),
        PolicyRule(
            rule_id="POL-003",
            description="Active output guardrails for Tier 2+",
            severity="blocking",
            check=lambda s: PolicyResult.PASS
                if s.get("risk_tier") == "tier_1"
                or s.get("output_guardrails_active", False)
                else PolicyResult.FAIL,
            remediation="Activate output guardrails before deployment"
        ),
        PolicyRule(
            rule_id="POL-004",
            description="Transparency card completed",
            severity="blocking",
            check=lambda s: PolicyResult.PASS
                if s.get("transparency_card_complete", False)
                else PolicyResult.FAIL,
            remediation="Complete AISystemCard (see Chapter 8)"
        ),
        PolicyRule(
            rule_id="POL-005",
            description="Human-in-the-loop for Tier 3",
            severity="blocking",
            check=lambda s: PolicyResult.PASS
                if s.get("risk_tier") != "tier_3"
                or s.get("human_in_the_loop", False)
                else PolicyResult.FAIL,
            remediation="Implement human oversight mechanism"
        ),
        PolicyRule(
            rule_id="POL-006",
            description="Provider model approved",
            severity="blocking",
            check=lambda s: PolicyResult.PASS
                if s.get("model_name") in APPROVED_MODELS
                else PolicyResult.FAIL,
            remediation="Request model approval from committee"
        ),
        PolicyRule(
            rule_id="POL-007",
            description="Interaction logging active",
            severity="warning",
            check=lambda s: PolicyResult.PASS
                if s.get("interaction_logging", False)
                else PolicyResult.WARN,
            remediation="Configure logging without PII capture"
        ),
    ]
    return rules

APPROVED_MODELS = [
    "claude-sonnet-4-6", "claude-haiku-4-5", "claude-opus-4-6",
    "gpt-4o", "gpt-4o-mini",
    "gemini-2.0-flash", "gemini-2.0-pro",
]

def _check_eval_currency(system: dict) -> PolicyResult:
    """Verifies that the security evaluation is current."""
    last_eval = system.get("last_security_eval")
    if not last_eval:
        return PolicyResult.FAIL
    
    max_days = {"tier_1": 90, "tier_2": 30, "tier_3": 7}
    tier = system.get("risk_tier", "tier_1")
    age = (datetime.utcnow() - last_eval).days
    
    if age > max_days.get(tier, 90):
        return PolicyResult.FAIL
    return PolicyResult.PASS

def evaluate_system(
    system: dict, 
    rules: list[PolicyRule]
) -> PolicyEvaluation:
    """Evaluates a system against all policy rules."""
    results = []
    for rule in rules:
        result = rule.check(system)
        results.append({
            "rule_id": rule.rule_id,
            "description": rule.description,
            "result": result.value,
            "severity": rule.severity,
            "remediation": rule.remediation 
                if result == PolicyResult.FAIL 
                else None
        })
    
    # Deployable = no blocking rules in FAIL
    blocking_fails = [
        r for r in results 
        if r["severity"] == "blocking" 
        and r["result"] == "fail"
    ]
    
    return PolicyEvaluation(
        system_name=system.get("name", "unknown"),
        timestamp=datetime.utcnow(),
        results=results,
        deployable=len(blocking_fails) == 0
    )

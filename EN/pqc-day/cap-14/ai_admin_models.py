"""
PQC-Day and the Machine — Chapter 14
Pattern: AI governance models — AIProvider, AIService, AIPrompt, AIUsageLog

This is a didactic example from the book, not production code.
See chapter 14 for full context and explanation.

These are standalone dataclass models that mirror the SQLAlchemy models
described in the book, suitable for reference and testing.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum


class ProviderType(str, Enum):
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    AZURE_AI_FOUNDRY = "azure_ai_foundry"
    GROQ = "groq"
    CUSTOM = "custom"


class ValidationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    APPROVED_WITH_CONDITIONS = "approved_with_conditions"
    REJECTED = "rejected"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class AIProvider:
    """LLM provider registry — replaces env var config with auditable records."""
    id: int = 0
    name: str = ""
    provider_type: str = "anthropic"
    endpoint: str = ""
    api_key_encrypted: str = ""         # Encrypted at application level
    default_model: str = ""
    is_default: bool = False
    is_active: bool = True

    # Aggregated metrics — updated by each usage_log write
    total_tokens_used: int = 0
    total_cost_usd: float = 0.0
    cost_per_1k_tokens_in: float = 0.0
    cost_per_1k_tokens_out: float = 0.0

    # Last connectivity test status
    last_test_status: str = "not_tested"  # success, failure, not_tested
    last_test_latency_ms: int = 0


@dataclass
class AIService:
    """Configurable AI service — temperature, model, and prompts per use case."""
    id: int = 0
    name: str = ""
    slug: str = ""                      # Key connecting code to config
    description: str = ""
    category: str = "General"           # General, Chat, Analysis, Compliance
    provider_id: int = 0
    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout_seconds: int = 120
    is_active: bool = True

    # AI compliance validation fields
    risk_level: str = "low"
    validation_status: str = "pending"
    approved_at: Optional[datetime] = None
    next_review_at: Optional[datetime] = None
    uses_personal_data: bool = False
    training_data_use_disabled: bool = True


@dataclass
class AIPrompt:
    """Versioned prompt — no prompt hardcoded in code."""
    id: int = 0
    service_id: int = 0
    role: str = "system"                # system, user, assistant
    name: str = ""
    content: str = ""
    language: str = "en"                # en, es
    version: int = 1
    is_active: bool = True
    created_by: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AIUsageLog:
    """Detailed log of each AI call — audit trail + cost tracking."""
    id: int = 0
    service_id: int = 0
    provider_id: int = 0
    user_id: int = 0
    model: str = ""
    operation: str = ""                 # 'chat', 'pqc_analysis', etc.
    tokens_in: int = 0
    tokens_out: int = 0
    tokens_total: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    status: str = "success"             # success, error, timeout
    error_message: str = ""
    request_hash: str = ""              # SHA-256 of prompt, for deduplication
    client_id: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AIGovernanceControl:
    """AI governance controls — C.VR.1 to C.VR.12 framework."""
    id: int = 0
    control_id: str = ""                # 'C.VR.1'
    category: str = ""                  # Privacy, Access, DLP, Audit, Governance
    name: str = ""
    description: str = ""
    requirement: str = ""
    status: str = "pending"             # compliant, partial, non_compliant, pending
    evidence: str = ""
    responsible: str = ""
    last_checked_at: Optional[datetime] = None
    next_check_at: Optional[datetime] = None


def get_active_prompt(services: List[AIService], prompts: List[AIPrompt],
                      service_slug: str, role: str = 'system',
                      language: str = 'en') -> str:
    """Get the active prompt for a service, role, and language."""
    service = next((s for s in services if s.slug == service_slug), None)
    if not service:
        raise ValueError(f"AI service '{service_slug}' not registered")

    # Find active prompt matching criteria
    matching = [
        p for p in prompts
        if p.service_id == service.id
        and p.role == role
        and p.language == language
        and p.is_active
    ]

    if not matching:
        # Fallback to any language
        matching = [
            p for p in prompts
            if p.service_id == service.id
            and p.role == role
            and p.is_active
        ]

    if not matching:
        raise ValueError(f"No active prompt for service '{service_slug}'")

    # Return highest version
    matching.sort(key=lambda p: p.version, reverse=True)
    return matching[0].content


def seed_governance_controls() -> List[AIGovernanceControl]:
    """Create the 12 controls of the rapid validation framework."""
    controls_data = [
        ('C.VR.1', 'Privacy',
         'Disable training data usage',
         'Disable the use of conversations for provider model training.'),
        ('C.VR.2', 'Privacy',
         'Defined retention policy',
         'Define and configure conversation retention period.'),
        ('C.VR.3', 'Access',
         'SSO + MFA authentication',
         'Require SSO and MFA for all users.'),
        ('C.VR.4', 'Access',
         'RBAC with least privilege',
         'Implement role-based access with minimal admin users.'),
        ('C.VR.5', 'Access',
         'Block external sharing',
         'Prevent external sharing of conversations and configs.'),
        ('C.VR.6', 'Governance',
         'Restricted AI config creation',
         'Limit AI config creation to authorized group.'),
        ('C.VR.7', 'DLP',
         'Connectors disabled by default',
         'Keep all connectors disabled with minimal scope.'),
        ('C.VR.8', 'DLP',
         'DLP rules configured',
         'Block upload of PII, IBANs, cards, tokens, private keys.'),
        ('C.VR.9', 'Audit',
         'Log export to SIEM',
         'Export audit logs to SIEM with defined retention.'),
        ('C.VR.10', 'Privacy',
         'Restricted data export',
         'Limit data export to authorized users only.'),
        ('C.VR.11', 'DLP',
         'File upload policy',
         'Control file upload with size limits and type validation.'),
        ('C.VR.12', 'Governance',
         'Periodic tenant review',
         'Monthly/quarterly review of permissions, connectors, roles.'),
    ]

    controls = []
    for i, (cid, cat, name, desc) in enumerate(controls_data, 1):
        controls.append(AIGovernanceControl(
            id=i, control_id=cid, category=cat,
            name=name, description=desc,
            status='pending', responsible='CISO'
        ))
    return controls


def calculate_roi(total_calls: int, total_cost_usd: float,
                  analyst_hourly_rate: float = 80.0,
                  minutes_saved_per_call: int = 20) -> Dict:
    """Calculate AI ROI: real cost vs. generated value."""
    hours_saved = total_calls * minutes_saved_per_call / 60
    value_generated = hours_saved * analyst_hourly_rate
    roi_ratio = round(value_generated / max(total_cost_usd, 0.01), 1)

    return {
        'total_cost_usd': round(total_cost_usd, 4),
        'estimated_hours_saved': round(hours_saved, 1),
        'estimated_value_eur': round(value_generated, 2),
        'roi_ratio': roi_ratio,
        'cost_per_call_usd': round(
            total_cost_usd / max(total_calls, 1), 6),
    }


# --- Main ---
if __name__ == '__main__':
    # Seed governance controls
    controls = seed_governance_controls()
    print("=== AI Governance Controls (C.VR.1 to C.VR.12) ===\n")
    for c in controls:
        print(f"  {c.control_id:6s} [{c.category:10s}] {c.name}")

    # Calculate sample ROI
    roi = calculate_roi(
        total_calls=1000,
        total_cost_usd=150.0,
        analyst_hourly_rate=80.0,
        minutes_saved_per_call=20
    )
    print(f"\n=== AI ROI Calculation ===")
    print(f"  Total calls: 1,000")
    print(f"  Total cost: ${roi['total_cost_usd']}")
    print(f"  Hours saved: {roi['estimated_hours_saved']}")
    print(f"  Value generated: EUR {roi['estimated_value_eur']}")
    print(f"  ROI ratio: {roi['roi_ratio']}:1")
    print(f"  Cost per call: ${roi['cost_per_call_usd']}")

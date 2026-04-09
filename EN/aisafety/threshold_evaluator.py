# Extracted from: LibroAISafety/ch-07-responsible-scaling.md
# threshold_evaluator.py — Risk level change evaluation
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import json
from datetime import datetime

class RiskTier(Enum):
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3

@dataclass
class SystemProfile:
    """Profile of an AI system for risk evaluation."""
    name: str
    has_pii_access: bool           # Access to personal data
    has_internal_data: bool        # Access to internal data
    can_modify_systems: bool       # Write/execute capability
    has_external_api_access: bool  # Access to external APIs
    is_autonomous: bool            # Operates without human supervision
    user_count: int                # Number of users
    model_provider: str            # Model provider
    model_name: str                # Specific model name

def evaluate_risk_tier(profile: SystemProfile) -> RiskTier:
    """
    Determines the risk level of an AI system
    based on its capabilities and access.
    """
    # Tier 3: any autonomous system with action capability
    if profile.is_autonomous and profile.can_modify_systems:
        return RiskTier.TIER_3
    
    # Tier 3: access to external payment APIs without supervision
    if profile.has_external_api_access and profile.is_autonomous:
        return RiskTier.TIER_3
    
    # Tier 2: access to internal data or modification capability
    if profile.has_internal_data or profile.can_modify_systems:
        return RiskTier.TIER_2
    
    # Tier 2: access to PII
    if profile.has_pii_access:
        return RiskTier.TIER_2
    
    # Tier 1: default
    return RiskTier.TIER_1

def check_tier_change(
    system_name: str,
    current_tier: RiskTier,
    new_profile: SystemProfile
) -> Optional[dict]:
    """
    Evaluates whether a change in the system profile
    requires risk level reclassification.
    """
    new_tier = evaluate_risk_tier(new_profile)
    
    if new_tier.value > current_tier.value:
        return {
            "system": system_name,
            "current_tier": current_tier.name,
            "proposed_tier": new_tier.name,
            "timestamp": datetime.utcnow().isoformat(),
            "action_required": "APPROVAL_NEEDED",
            "reason": _build_reason(current_tier, new_tier, new_profile),
            "additional_controls": _get_new_controls(
                current_tier, new_tier
            )
        }
    return None  # No level change

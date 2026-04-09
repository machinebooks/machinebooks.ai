# Extracted from: LibroAISafety/ch-09-regulation.md
# regulatory_inventory.py — AI system ↔ applicable regulation mapping
from dataclasses import dataclass
from enum import Enum

class AIActRisk(Enum):
    UNACCEPTABLE = "unacceptable"
    HIGH = "high"
    LIMITED = "limited"
    MINIMAL = "minimal"

class Jurisdiction(Enum):
    EU = "eu"
    US = "us"
    GLOBAL = "global"

@dataclass
class RegulatoryProfile:
    """Regulatory profile of an AI system."""
    system_name: str
    jurisdictions: list[Jurisdiction]
    ai_act_risk: AIActRisk
    nist_applicable: bool
    sector_regulations: list[str]  # GDPR, DORA, NIS2...
    
    def required_controls(self) -> list[str]:
        """
        Returns mandatory controls according to
        applicable regulations.
        """
        controls = []
        
        # AI Act — high risk
        if self.ai_act_risk == AIActRisk.HIGH:
            controls.extend([
                "risk_management_system",      # Art. 9
                "data_governance",              # Art. 10
                "technical_documentation",      # Art. 11
                "record_keeping",               # Art. 12
                "transparency_notice",          # Art. 13
                "human_oversight",              # Art. 14
                "accuracy_robustness_security", # Art. 15
                "post_market_monitoring",       # Art. 72
                "eu_database_registration",     # Art. 71
                "conformity_assessment",        # Art. 43
            ])
        
        # AI Act — limited risk
        elif self.ai_act_risk == AIActRisk.LIMITED:
            controls.extend([
                "transparency_notice",  # Inform the user
                "ai_generated_marking", # Mark generated content
            ])
        
        # NIST AI RMF (voluntary but recommended)
        if self.nist_applicable:
            controls.extend([
                "nist_govern_policies",
                "nist_map_risk_identification",
                "nist_measure_metrics",
                "nist_manage_controls",
            ])
        
        # Sector regulations
        if "GDPR" in self.sector_regulations:
            controls.extend([
                "dpia",                    # Impact assessment
                "data_minimization",
                "right_to_explanation",
            ])
        
        if "DORA" in self.sector_regulations:
            controls.extend([
                "ict_risk_management",
                "incident_reporting",
                "digital_resilience_testing",
            ])
        
        return list(set(controls))  # Remove duplicates

def classify_ai_act_risk(
    use_case: str,
    sector: str,
    user_facing: bool,
    affects_rights: bool
) -> AIActRisk:
    """
    Simplified AI Act risk classification.
    In production, this decision requires legal counsel.
    """
    # Prohibited practices (simplified)
    prohibited_uses = [
        "social_scoring", "subliminal_manipulation",
        "real_time_biometric_public"
    ]
    if use_case in prohibited_uses:
        return AIActRisk.UNACCEPTABLE
    
    # High-risk sectors (AI Act Annex III)
    high_risk_sectors = [
        "employment", "education", "law_enforcement",
        "migration", "justice", "critical_infrastructure",
        "essential_services", "credit_scoring"
    ]
    if sector in high_risk_sectors and affects_rights:
        return AIActRisk.HIGH
    
    # Systems that interact with people
    if user_facing:
        return AIActRisk.LIMITED
    
    return AIActRisk.MINIMAL

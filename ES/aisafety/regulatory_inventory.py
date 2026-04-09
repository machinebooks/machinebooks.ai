# Extraido de: LibroAISafety/cap-09-regulacion.md
# regulatory_inventory.py — Mapeo sistema IA ↔ regulación aplicable
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
    """Perfil regulatorio de un sistema de IA."""
    system_name: str
    jurisdictions: list[Jurisdiction]
    ai_act_risk: AIActRisk
    nist_applicable: bool
    sector_regulations: list[str]  # GDPR, DORA, NIS2...
    
    def required_controls(self) -> list[str]:
        """
        Devuelve los controles obligatorios según
        las regulaciones aplicables.
        """
        controls = []
        
        # AI Act — alto riesgo
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
        
        # AI Act — riesgo limitado
        elif self.ai_act_risk == AIActRisk.LIMITED:
            controls.extend([
                "transparency_notice",  # Informar al usuario
                "ai_generated_marking", # Marcar contenido generado
            ])
        
        # NIST AI RMF (voluntario pero recomendado)
        if self.nist_applicable:
            controls.extend([
                "nist_govern_policies",
                "nist_map_risk_identification",
                "nist_measure_metrics",
                "nist_manage_controls",
            ])
        
        # Regulaciones sectoriales
        if "GDPR" in self.sector_regulations:
            controls.extend([
                "dpia",                    # Evaluación de impacto
                "data_minimization",
                "right_to_explanation",
            ])
        
        if "DORA" in self.sector_regulations:
            controls.extend([
                "ict_risk_management",
                "incident_reporting",
                "digital_resilience_testing",
            ])
        
        return list(set(controls))  # Eliminar duplicados

def classify_ai_act_risk(
    use_case: str,
    sector: str,
    user_facing: bool,
    affects_rights: bool
) -> AIActRisk:
    """
    Clasificación simplificada de riesgo AI Act.
    En producción, esta decisión requiere asesoría legal.
    """
    # Prácticas prohibidas (simplificado)
    prohibited_uses = [
        "social_scoring", "subliminal_manipulation",
        "real_time_biometric_public"
    ]
    if use_case in prohibited_uses:
        return AIActRisk.UNACCEPTABLE
    
    # Sectores de alto riesgo (Anexo III del AI Act)
    high_risk_sectors = [
        "employment", "education", "law_enforcement",
        "migration", "justice", "critical_infrastructure",
        "essential_services", "credit_scoring"
    ]
    if sector in high_risk_sectors and affects_rights:
        return AIActRisk.HIGH
    
    # Sistemas que interactúan con personas
    if user_facing:
        return AIActRisk.LIMITED
    
    return AIActRisk.MINIMAL

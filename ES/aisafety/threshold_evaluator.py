# Extraido de: LibroAISafety/cap-07-responsible-scaling.md
# threshold_evaluator.py — Evaluación de cambio de nivel de riesgo
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
    """Perfil de un sistema de IA para evaluación de riesgo."""
    name: str
    has_pii_access: bool           # Acceso a datos personales
    has_internal_data: bool        # Acceso a datos internos
    can_modify_systems: bool       # Capacidad de escritura/ejecución
    has_external_api_access: bool  # Acceso a APIs externas
    is_autonomous: bool            # Opera sin supervisión humana
    user_count: int                # Número de usuarios
    model_provider: str            # Proveedor del modelo
    model_name: str                # Nombre específico del modelo

def evaluate_risk_tier(profile: SystemProfile) -> RiskTier:
    """
    Determina el nivel de riesgo de un sistema de IA
    según sus capacidades y accesos.
    """
    # Tier 3: cualquier sistema autónomo con capacidad de acción
    if profile.is_autonomous and profile.can_modify_systems:
        return RiskTier.TIER_3
    
    # Tier 3: acceso a APIs externas de pago sin supervisión
    if profile.has_external_api_access and profile.is_autonomous:
        return RiskTier.TIER_3
    
    # Tier 2: acceso a datos internos o capacidad de modificación
    if profile.has_internal_data or profile.can_modify_systems:
        return RiskTier.TIER_2
    
    # Tier 2: acceso a PII
    if profile.has_pii_access:
        return RiskTier.TIER_2
    
    # Tier 1: por defecto
    return RiskTier.TIER_1

def check_tier_change(
    system_name: str,
    current_tier: RiskTier,
    new_profile: SystemProfile
) -> Optional[dict]:
    """
    Evalúa si un cambio en el perfil del sistema
    requiere reclasificación de nivel.
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
    return None  # Sin cambio de nivel

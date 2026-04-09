# Extraido de: LibroAISafety/cap-08-transparencia.md
# ai_system_card.py — Ficha de transparencia para sistemas IA internos
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class AISystemCard:
    """
    Ficha de transparencia para un sistema de IA en producción.
    Una por sistema. Obligatoria antes del despliegue.
    """
    # Identificación
    system_name: str
    system_id: str
    owner_team: str
    deployment_date: Optional[datetime] = None
    last_review_date: Optional[datetime] = None
    
    # Modelo
    model_provider: str = ""         # "anthropic", "openai", "meta"
    model_name: str = ""             # "claude-sonnet-4-6"
    model_version: str = ""          # Versión específica
    system_card_url: str = ""        # URL a la System Card del modelo
    
    # Uso
    purpose: str = ""                # Descripción del caso de uso
    user_facing: bool = False        # ¿Interactúa directamente con usuarios?
    user_count: int = 0
    daily_interactions: int = 0
    
    # Datos
    data_sources: list[str] = field(default_factory=list)
    pii_processed: bool = False
    data_retention_days: int = 0
    
    # Riesgo y controles
    risk_tier: str = ""              # "tier_1", "tier_2", "tier_3"
    controls_implemented: list[str] = field(default_factory=list)
    last_security_eval: Optional[datetime] = None
    known_limitations: list[str] = field(default_factory=list)
    
    # Incidentes
    incident_count_30d: int = 0
    last_incident_date: Optional[datetime] = None
    
    def compliance_status(self) -> dict:
        """Verifica completitud de la ficha."""
        required_fields = [
            self.system_name, self.model_provider,
            self.model_name, self.purpose, self.risk_tier
        ]
        missing = [
            f for f in ["name", "provider", "model", 
                        "purpose", "risk_tier"]
            if not getattr(self, {
                "name": "system_name",
                "provider": "model_provider",
                "model": "model_name",
                "purpose": "purpose",
                "risk_tier": "risk_tier"
            }[f])
        ]
        return {
            "complete": len(missing) == 0,
            "missing_fields": missing,
            "has_security_eval": self.last_security_eval is not None,
            "has_limitations": len(self.known_limitations) > 0
        }

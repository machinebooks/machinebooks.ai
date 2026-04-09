# Extracted from: LibroAISafety/ch-08-transparency.md
# ai_system_card.py — Transparency card for internal AI systems
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class AISystemCard:
    """
    Transparency card for an AI system in production.
    One per system. Mandatory before deployment.
    """
    # Identification
    system_name: str
    system_id: str
    owner_team: str
    deployment_date: Optional[datetime] = None
    last_review_date: Optional[datetime] = None
    
    # Model
    model_provider: str = ""         # "anthropic", "openai", "meta"
    model_name: str = ""             # "claude-sonnet-4-6"
    model_version: str = ""          # Specific version
    system_card_url: str = ""        # URL to the model's System Card
    
    # Usage
    purpose: str = ""                # Use case description
    user_facing: bool = False        # Does it interact directly with users?
    user_count: int = 0
    daily_interactions: int = 0
    
    # Data
    data_sources: list[str] = field(default_factory=list)
    pii_processed: bool = False
    data_retention_days: int = 0
    
    # Risk and controls
    risk_tier: str = ""              # "tier_1", "tier_2", "tier_3"
    controls_implemented: list[str] = field(default_factory=list)
    last_security_eval: Optional[datetime] = None
    known_limitations: list[str] = field(default_factory=list)
    
    # Incidents
    incident_count_30d: int = 0
    last_incident_date: Optional[datetime] = None
    
    def compliance_status(self) -> dict:
        """Verifies card completeness."""
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

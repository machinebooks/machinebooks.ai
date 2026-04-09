# Extraido de: LibroAISafety/cap-10-governance-operativa.md
# ai_asset_inventory.py — Inventario de activos de IA
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class AIAssetInventory:
    """Inventario centralizado de activos de IA."""
    
    models: list[dict] = field(default_factory=list)
    api_keys: list[dict] = field(default_factory=list)
    mcp_servers: list[dict] = field(default_factory=list)
    rag_collections: list[dict] = field(default_factory=list)
    system_prompts: list[dict] = field(default_factory=list)

    def audit_stale_assets(self, max_age_days: int = 90) -> list[dict]:
        """Identifica activos sin revisión reciente."""
        stale = []
        now = datetime.utcnow()
        for model in self.models:
            last_eval = model.get("last_security_eval")
            if last_eval and (now - last_eval).days > max_age_days:
                stale.append({
                    "type": "model", "name": model["name"],
                    "days_since_eval": (now - last_eval).days
                })
        for key in self.api_keys:
            last_rotation = key.get("last_rotated")
            if last_rotation and (now - last_rotation).days > max_age_days:
                stale.append({
                    "type": "api_key", "name": key["key_id"],
                    "days_since_rotation": (now - last_rotation).days
                })
        return stale

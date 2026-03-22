# Source: The FinOps Engineer and the Machine -- Chapter 22
# Pattern: Model lifecycle management

# services/model_lifecycle.py
from sqlalchemy.orm import Session
from models.llm_pricing import LLMModelPricing


class ModelLifecycleManager:
    """
    Manages transitions between LLM model versions.
    Enables pilots with partial traffic and immediate rollback.
    """

    def configure_traffic_split(
        self,
        db: Session,
        current_model_id: str,
        new_model_id: str,
        new_model_traffic_pct: float,  # 0.0-1.0
    ) -> dict:
        current = db.query(LLMModelPricing).filter(
            LLMModelPricing.model_id == current_model_id
        ).first()
        new = db.query(LLMModelPricing).filter(
            LLMModelPricing.model_id == new_model_id
        ).first()

        if not current or not new:
            raise ValueError("Model not found in configuration")

        # Lower priority = more traffic
        current.priority = int((1.0 - new_model_traffic_pct) * 100)
        new.priority = int(new_model_traffic_pct * 100)
        new.active = True
        db.commit()

        return {
            "current_model": current_model_id,
            "current_traffic_pct": round((1 - new_model_traffic_pct) * 100),
            "new_model": new_model_id,
            "new_traffic_pct": round(new_model_traffic_pct * 100),
        }

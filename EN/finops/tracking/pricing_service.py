# Source: The FinOps Engineer and the Machine -- Chapter 2
# Pattern: PricingService with fallback and unknown model logging

# services/pricing_service.py
# Pricing query service with fallback and unknown model logging.

from sqlalchemy.orm import Session
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PricingService:
    """
    Queries the LLMModelPricing table and calculates LLM call costs.
    Design: stateless, instantiated per request or used as singleton.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_active_pricing(
        self,
        provider: str,
        model_id: str
    ) -> Optional[LLMModelPricing]:
        """
        Returns the active pricing record for a model.
        Orders by effective_date DESC to get the most recent.
        """
        return (
            self.db.query(LLMModelPricing)
            .filter(
                LLMModelPricing.provider == provider,
                LLMModelPricing.model_id == model_id,
                LLMModelPricing.is_active == True,
            )
            .order_by(LLMModelPricing.effective_date.desc())
            .first()
        )

    def cost_for_call(
        self,
        provider: str,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
        cached_input_tokens: int = 0,
        cache_write_tokens: int = 0,
        eur_exchange_rate: float = 0.92,
    ) -> Optional[CallCostBreakdown]:
        """
        Main entry point for calculating the cost of a call.
        Returns None if the model is not in the table (and emits a warning).
        """
        pricing = self.get_active_pricing(provider, model_id)

        if pricing is None:
            # Model not in the table: we log it but do not block.
            # The call will have happened anyway; the cost remains uncalculated.
            logger.warning(
                "Model not found in pricing table. "
                "provider=%s model_id=%s tokens_input=%d tokens_output=%d. "
                "Add record to LLMModelPricing to enable tracking.",
                provider, model_id, input_tokens, output_tokens
            )
            return None

        return calculate_call_cost(
            pricing=pricing,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_input_tokens=cached_input_tokens,
            cache_write_tokens=cache_write_tokens,
            eur_exchange_rate=eur_exchange_rate,
        )

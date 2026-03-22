# Source: The FinOps Engineer and the Machine -- Chapter 8
# Pattern: Model router -- route tasks to cheapest capable model

# services/model_router.py (continued)
from sqlalchemy.orm import Session
from models.llm_config import LLMServiceConfig, ModelTier, TIER_TO_MODEL
import logging

logger = logging.getLogger(__name__)

class ModelRouter:
    """
    Selects the optimal model for each LLM call.
    Combines the service configuration with the heuristic estimate.
    """

    def __init__(self, db: Session):
        self.db = db
        self._config_cache: dict[str, LLMServiceConfig] = {}

    def _get_service_config(self, service_name: str) -> Optional[LLMServiceConfig]:
        """Loads the service config with in-memory cache."""
        if service_name not in self._config_cache:
            config = (
                self.db.query(LLMServiceConfig)
                .filter(LLMServiceConfig.service_name == service_name)
                .first()
            )
            if config:
                self._config_cache[service_name] = config
        return self._config_cache.get(service_name)

    def select_model(
        self,
        service_name: str,
        routing_ctx: Optional[RoutingContext] = None,
    ) -> str:
        """
        Returns the model name that should be used for this call.

        Logic:
          1. If the service has config, start from the default tier.
          2. If allow_upgrade or allow_downgrade, apply the classifier.
          3. Map tier to model name.
        """
        config = self._get_service_config(service_name)

        if config is None:
            # Unconfigured service → use balanced as safe fallback
            logger.warning("Service '%s' has no routing config; using balanced", service_name)
            return TIER_TO_MODEL[ModelTier.BALANCED]

        tier = config.default_tier

        # Apply heuristic classifier if context is available
        if routing_ctx is not None and (config.allow_upgrade or config.allow_downgrade):
            estimated = estimate_complexity(routing_ctx)

            if config.allow_upgrade and estimated.value > tier.value:
                logger.info(
                    "Routing upgrade: %s %s → %s", service_name, tier, estimated
                )
                tier = estimated

            elif config.allow_downgrade and estimated.value < tier.value:
                logger.info(
                    "Routing downgrade: %s %s → %s", service_name, tier, estimated
                )
                tier = estimated

        model = TIER_TO_MODEL[tier]
        logger.debug("Routing: service=%s tier=%s model=%s", service_name, tier, model)
        return model

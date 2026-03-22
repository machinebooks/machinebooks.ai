# Extraído de: LibroFinOps/cap-08-routing-modelos.md
# services/model_router.py (continuación)
from sqlalchemy.orm import Session
from models.llm_config import LLMServiceConfig, ModelTier, TIER_TO_MODEL
import logging

logger = logging.getLogger(__name__)

class ModelRouter:
    """
    Selecciona el modelo óptimo para cada llamada LLM.
    Combina la configuración de servicio con la estimación heurística.
    """

    def __init__(self, db: Session):
        self.db = db
        self._config_cache: dict[str, LLMServiceConfig] = {}

    def _get_service_config(self, service_name: str) -> Optional[LLMServiceConfig]:
        """Carga la config del servicio con caché en memoria."""
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
        Devuelve el nombre del modelo que debe usarse para esta llamada.

        Lógica:
          1. Si el servicio tiene config, partir del tier por defecto.
          2. Si allow_upgrade o allow_downgrade, aplicar el clasificador.
          3. Mapear tier a nombre de modelo.
        """
        config = self._get_service_config(service_name)

        if config is None:
            # Servicio no configurado → usar balanced como fallback seguro
            logger.warning("Servicio '%s' sin config de routing; usando balanced", service_name)
            return TIER_TO_MODEL[ModelTier.BALANCED]

        tier = config.default_tier

        # Aplicar clasificador heurístico si hay contexto disponible
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

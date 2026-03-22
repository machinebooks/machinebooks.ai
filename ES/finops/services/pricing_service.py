# Extraído de: LibroFinOps/cap-02-anatomia-coste.md
# services/pricing_service.py
# Servicio de consulta de precios con fallback y logging de modelo desconocido.

from sqlalchemy.orm import Session
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PricingService:
    """
    Consulta la tabla LLMModelPricing y calcula costes de llamadas LLM.
    Diseño: stateless, se instancia por request o se usa como singleton.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_active_pricing(
        self,
        provider: str,
        model_id: str
    ) -> Optional[LLMModelPricing]:
        """
        Devuelve el registro de precio activo para un modelo.
        Ordena por effective_date DESC para obtener el más reciente.
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
        Punto de entrada principal para calcular el coste de una llamada.
        Devuelve None si el modelo no está en la tabla (y emite un warning).
        """
        pricing = self.get_active_pricing(provider, model_id)

        if pricing is None:
            # El modelo no está en la tabla: lo registramos pero no bloqueamos.
            # La llamada habrá ocurrido igual; el coste queda sin calcular.
            logger.warning(
                "Modelo no encontrado en tabla de precios. "
                "provider=%s model_id=%s tokens_input=%d tokens_output=%d. "
                "Añadir registro a LLMModelPricing para habilitar tracking.",
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

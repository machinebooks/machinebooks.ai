# Extraído de: LibroFinOps/cap-22-multiproveedor.md
# services/llm_router.py
from typing import Optional
import anthropic
from sqlalchemy.orm import Session
from models.llm_pricing import LLMModelPricing
from services.failover import get_best_available_model
from services.policy_reconciler import PolicyReconciler
import logging

logger = logging.getLogger(__name__)


class LLMRouter:
    """Router central. Combina política FinOps, health check, y failover."""

    def __init__(self, db: Session):
        self.db = db
        self.policy = PolicyReconciler()

    async def route_and_call(
        self,
        messages: list,
        task_type: str,
        tenant_id: str,
        system_prompt: Optional[str] = None,
        min_context_tokens: int = 0,
    ) -> dict:
        # 1. Consultar política FinOps (modelo + límites)
        decision = self.policy.check_request(
            tenant_id=tenant_id, task_type=task_type,
        )
        if not decision["allowed"]:
            return {"error": "budget_exceeded", "detail": decision["reason"]}

        # 2. Verificar que el modelo está disponible (failover si no)
        model = self._get_model(decision["model"])
        if not model or model.health_status == "down":
            model = get_best_available_model(
                self.db, task_type, min_context_tokens,
            )
            if not model:
                return {"error": "no_providers_available"}

        # 3. Llamar al proveedor y calcular coste
        response = await self._call_provider(model, messages, system_prompt)
        cost = self._calculate_cost(model, response)
        return {**response, "provider": model.provider, "cost_usd": cost}

    def _calculate_cost(self, model: LLMModelPricing, resp: dict) -> float:
        """Calcula coste con precios actuales y descuento committed use."""
        input_cost = (resp["input_tokens"] / 1_000_000) * model.price_input_per_1m
        output_cost = (resp["output_tokens"] / 1_000_000) * model.price_output_per_1m
        total = input_cost + output_cost
        if model.committed_use_discount:
            total *= (1 - model.committed_use_discount)
        return round(total, 8)

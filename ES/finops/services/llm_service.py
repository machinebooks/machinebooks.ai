# Extraído de: LibroFinOps/cap-11-presupuestos-circuit-breakers.md
# services/llm_service.py (versión completa con presupuestos y circuit breaker)
import anthropic
from services.model_router import ModelRouter, RoutingContext
from services.usage_tracker import LLMUsageTracker
from middleware.budget_enforcement import (
    BudgetEnforcementMiddleware, BudgetExceededException
)
from services.financial_circuit_breaker import ProviderCircuitBreaker

class LLMService:
    """Servicio LLM con routing, presupuestos y circuit breaker integrados."""

    def __init__(
        self,
        db,
        router:       ModelRouter,
        tracker:      LLMUsageTracker,
        budget:       BudgetEnforcementMiddleware,
        cb_anthropic: ProviderCircuitBreaker,
    ):
        self.client   = anthropic.Anthropic()
        self.router   = router
        self.tracker  = tracker
        self.budget   = budget
        self.cb       = cb_anthropic

    async def complete(
        self,
        service_name:    str,
        prompt:          str,
        system:          str = "",
        user_id:         str | None = None,
        num_documents:   int = 0,
        expected_output: str = "text",
    ) -> str:
        """
        Llamada LLM con todos los controles de coste activos:
        1. Circuit breaker (¿está el proveedor en modo spike?)
        2. Budget check (¿hay presupuesto disponible?)
        3. Llamada al modelo
        4. Registro de uso y actualización de presupuesto
        5. Actualización del circuit breaker
        """

        # 1. Comprobar circuit breaker (coste: 0, solo lectura de estado en memoria)
        if not self.cb.allow_request():
            raise ServiceUnavailableException(
                "Proveedor LLM temporalmente no disponible (circuit breaker abierto). "
                "Reintentar en 5 minutos."
            )

        # 2. Seleccionar modelo mediante routing
        ctx   = RoutingContext(prompt_text=prompt, num_documents=num_documents,
                               expected_output=expected_output)
        model = self.router.select_model(service_name, ctx)

        # 3. Estimar coste para el pre-check de presupuesto
        # Estimación conservadora: 1.5× los tokens de entrada esperados
        estimated_cost = self._estimate_cost(model, len(prompt.split()) * 1.5)

        # 4. Comprobar y aplicar enforcement de presupuesto
        # (puede añadir delay por throttle o lanzar BudgetExceededException)
        await self.budget.check_and_enforce(service_name, user_id, estimated_cost)

        # 5. Ejecutar la llamada LLM
        response = self.client.messages.create(
            model=     model,
            max_tokens=1024,
            system=    system,
            messages=  [{"role": "user", "content": prompt}],
        )

        # 6. Calcular coste real (post-llamada)
        real_cost = self._calculate_cost(
            model,
            response.usage.input_tokens,
            response.usage.output_tokens,
        )

        # 7. Registrar uso en LLMUsageLog
        await self.tracker.record(
            service=       service_name,
            model=         model,
            input_tokens=  response.usage.input_tokens,
            output_tokens= response.usage.output_tokens,
            cost_usd=      real_cost,
            user_id=       user_id,
        )

        # 8. Actualizar presupuestos con el coste real
        self.budget.record_spend(
            config_ids=self.budget.get_applicable_config_ids(service_name, user_id),
            cost_usd=real_cost,
        )

        # 9. Actualizar circuit breaker con el coste real
        self.cb.record_success(real_cost)

        return response.content[0].text

    @staticmethod
    def _estimate_cost(model: str, estimated_tokens: float) -> float:
        """Estimación rápida de coste pre-llamada (solo entrada, sin salida)."""
        input_prices = {
            "claude-haiku-4-5":  0.80,
            "claude-sonnet-4-6": 3.00,
            "claude-opus-4-6":   15.00,
        }
        price = input_prices.get(model, 3.00)
        return estimated_tokens / 1_000_000 * price

    @staticmethod
    def _calculate_cost(model: str, input_t: int, output_t: int) -> float:
        """Cálculo exacto de coste post-llamada."""
        prices = {
            "claude-haiku-4-5":  (0.80,  4.00),
            "claude-sonnet-4-6": (3.00,  15.00),
            "claude-opus-4-6":   (15.00, 75.00),
        }
        ip, op = prices.get(model, (3.00, 15.00))
        return input_t / 1_000_000 * ip + output_t / 1_000_000 * op


class ServiceUnavailableException(Exception):
    """El servicio LLM no está disponible por circuit breaker abierto."""
    pass

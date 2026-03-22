# Source: The FinOps Engineer and the Machine -- Chapter 11
# Pattern: LLM service with budget + circuit breaker

# services/llm_service.py (complete version with budgets and circuit breaker)
import anthropic
from services.model_router import ModelRouter, RoutingContext
from services.usage_tracker import LLMUsageTracker
from middleware.budget_enforcement import (
    BudgetEnforcementMiddleware, BudgetExceededException
)
from services.financial_circuit_breaker import ProviderCircuitBreaker

class LLMService:
    """LLM service with integrated routing, budgets, and circuit breaker."""

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
        LLM call with all cost controls active:
        1. Circuit breaker (is the provider in spike mode?)
        2. Budget check (is there available budget?)
        3. Model call
        4. Usage recording and budget update
        5. Circuit breaker update
        """

        # 1. Check circuit breaker (cost: 0, read-only in-memory state)
        if not self.cb.allow_request():
            raise ServiceUnavailableException(
                "LLM provider temporarily unavailable (circuit breaker open). "
                "Retry in 5 minutes."
            )

        # 2. Select model via routing
        ctx   = RoutingContext(prompt_text=prompt, num_documents=num_documents,
                               expected_output=expected_output)
        model = self.router.select_model(service_name, ctx)

        # 3. Estimate cost for budget pre-check
        # Conservative estimate: 1.5× the expected input tokens
        estimated_cost = self._estimate_cost(model, len(prompt.split()) * 1.5)

        # 4. Check and apply budget enforcement
        # (may add delay for throttle or raise BudgetExceededException)
        await self.budget.check_and_enforce(service_name, user_id, estimated_cost)

        # 5. Execute the LLM call
        response = self.client.messages.create(
            model=     model,
            max_tokens=1024,
            system=    system,
            messages=  [{"role": "user", "content": prompt}],
        )

        # 6. Calculate real cost (post-call)
        real_cost = self._calculate_cost(
            model,
            response.usage.input_tokens,
            response.usage.output_tokens,
        )

        # 7. Record usage in LLMUsageLog
        await self.tracker.record(
            service=       service_name,
            model=         model,
            input_tokens=  response.usage.input_tokens,
            output_tokens= response.usage.output_tokens,
            cost_usd=      real_cost,
            user_id=       user_id,
        )

        # 8. Update budgets with real cost
        self.budget.record_spend(
            config_ids=self.budget.get_applicable_config_ids(service_name, user_id),
            cost_usd=real_cost,
        )

        # 9. Update circuit breaker with real cost
        self.cb.record_success(real_cost)

        return response.content[0].text

    @staticmethod
    def _estimate_cost(model: str, estimated_tokens: float) -> float:
        """Quick pre-call cost estimate (input only, no output)."""
        input_prices = {
            "claude-haiku-4-5":  0.80,
            "claude-sonnet-4-6": 3.00,
            "claude-opus-4-6":   15.00,
        }
        price = input_prices.get(model, 3.00)
        return estimated_tokens / 1_000_000 * price

    @staticmethod
    def _calculate_cost(model: str, input_t: int, output_t: int) -> float:
        """Exact post-call cost calculation."""
        prices = {
            "claude-haiku-4-5":  (0.80,  4.00),
            "claude-sonnet-4-6": (3.00,  15.00),
            "claude-opus-4-6":   (15.00, 75.00),
        }
        ip, op = prices.get(model, (3.00, 15.00))
        return input_t / 1_000_000 * ip + output_t / 1_000_000 * op


class ServiceUnavailableException(Exception):
    """LLM service unavailable due to open circuit breaker."""
    pass

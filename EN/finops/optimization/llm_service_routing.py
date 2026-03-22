# Source: The FinOps Engineer and the Machine -- Chapter 8
# Pattern: LLM service with routing integration

# services/llm_service.py
import anthropic
from services.model_router import ModelRouter, RoutingContext
from services.usage_tracker import LLMUsageTracker

class LLMService:
    """Central LLM call service with integrated routing and tracking."""

    def __init__(self, db, router: ModelRouter, tracker: LLMUsageTracker):
        self.client = anthropic.Anthropic()
        self.router = router
        self.tracker = tracker

    async def complete(
        self,
        service_name: str,
        prompt: str,
        system: str = "",
        num_documents: int = 0,
        expected_output: str = "text",
        user_id: Optional[str] = None,
    ) -> str:
        """LLM call with automatic routing and usage recording."""

        # 1. Determine model according to routing
        ctx = RoutingContext(
            prompt_text=prompt,
            num_documents=num_documents,
            expected_output=expected_output,
        )
        model = self.router.select_model(service_name, ctx)

        # 2. Call the selected model
        response = self.client.messages.create(
            model=model,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )

        # 3. Record usage with the actual model used (not the default)
        await self.tracker.record(
            service=service_name,
            model=model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            user_id=user_id,
        )

        return response.content[0].text

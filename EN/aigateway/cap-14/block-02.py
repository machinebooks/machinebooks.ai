# Extracted from: LibroAIGateway/cap-14-pricing-cost-roi.md
@classmethod
async def calculate_breakdown(
    cls, model: str, prompt_tokens: int, completion_tokens: int, db: AsyncSession,
    *, cached_tokens: int = 0, reasoning_tokens: int = 0,
    organization_id: int | None = None,
) -> CostBreakdown | None:
    rates = await cls._get_rates(model, db, organization_id=organization_id)
    if not rates:
        return None

    # Sanitize: they cannot exceed the total
    cached = max(0, min(cached_tokens, prompt_tokens))
    reasoning = max(0, min(reasoning_tokens, completion_tokens))

    non_cached = Decimal(prompt_tokens - cached)
    non_reasoning = Decimal(completion_tokens - reasoning)
    per_1k = Decimal(1000)

    input_dec     = (non_cached     / per_1k) * rates.prompt
    cached_dec_v  = (cached_dec     / per_1k) * rates.effective_cached()
    output_dec    = (non_reasoning  / per_1k) * rates.output
    reasoning_dec_v = (reasoning_dec / per_1k) * rates.effective_reasoning()

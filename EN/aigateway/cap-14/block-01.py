# Extracted from: LibroAIGateway/cap-14-pricing-cost-roi.md
@dataclass(frozen=True)
class PricingRates:
    prompt: Decimal
    cached_input: Decimal | None
    output: Decimal
    reasoning_output: Decimal | None

    def effective_cached(self) -> Decimal:
        # NULL or 0 means "no discount → use prompt price"
        if self.cached_input is None or self.cached_input == 0:
            return self.prompt
        return self.cached_input

    def effective_reasoning(self) -> Decimal:
        # NULL or 0 means "bundled in output → use output price"
        if self.reasoning_output is None or self.reasoning_output == 0:
            return self.output
        return self.reasoning_output

# Extraído de: LibroAIGateway/cap-14-pricing-cost-roi.md
@dataclass(frozen=True)
class PricingRates:
    prompt: Decimal
    cached_input: Decimal | None
    output: Decimal
    reasoning_output: Decimal | None

    def effective_cached(self) -> Decimal:
        # NULL o 0 significa "sin descuento → usar precio prompt"
        if self.cached_input is None or self.cached_input == 0:
            return self.prompt
        return self.cached_input

    def effective_reasoning(self) -> Decimal:
        # NULL o 0 significa "bundled en output → usar precio output"
        if self.reasoning_output is None or self.reasoning_output == 0:
            return self.output
        return self.reasoning_output

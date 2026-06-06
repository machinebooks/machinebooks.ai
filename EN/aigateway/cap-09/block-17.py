# Extracted from: LibroAIGateway/cap-09-compression-tokens.md
# gateway/app/services/token_counter.py:303-326 (synthesized)
def preflight_check(
    *, model: str, estimated_input_tokens: int,
    max_output_tokens: int, safety_margin: int = 256,
) -> None:
    window = get_context_window(model)
    if window is None:
        return  # unknown model → delegate to provider
    total = estimated_input_tokens + max_output_tokens + safety_margin
    if total >= window:
        raise TokenBudgetExceeded(
            estimated_input=estimated_input_tokens,
            max_output=max_output_tokens,
            context_window=window, model=model,
        )

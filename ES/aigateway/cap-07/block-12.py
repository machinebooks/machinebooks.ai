# Extraído de: LibroAIGateway/cap-07-adapters.md
def _normalized_thinking_and_max_tokens(max_allowed, thinking, requested_max):
    budget = _thinking_budget_tokens(thinking)
    budget = min(budget, max_allowed - 1)       # budget < max_tokens
    max_tokens = min(max(requested_max, budget + 1), max_allowed)
    return {"type": "enabled", "budget_tokens": budget}, max_tokens, budget

# Extraído de: LibroFinOps/cap-04-instrumentacion-llm.md
# services/llm_pricing.py
from typing import TypedDict

class CostBreakdown(TypedDict):
    input: float
    output: float
    cache: float
    total: float

# Precios en USD por millón de tokens (actualizar cuando cambien)
MODEL_PRICING = {
    "claude-opus-4-6": {
        "input": 15.00,
        "output": 75.00,
        "cache_creation": 18.75,   # 125% del precio de input
        "cache_read": 1.50,        # 10% del precio de input
    },
    "claude-sonnet-4-6": {
        "input": 3.00,
        "output": 15.00,
        "cache_creation": 3.75,
        "cache_read": 0.30,
    },
    "claude-haiku-4-5": {
        "input": 0.80,
        "output": 4.00,
        "cache_creation": 1.00,
        "cache_read": 0.08,
    },
}

def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_creation_tokens: int = 0,
    cache_read_tokens: int = 0,
) -> CostBreakdown:
    """
    Calcula el coste en USD de una llamada LLM.
    Los tokens cacheados se cargan a precio reducido.
    Los tokens de cache_read son los de mayor ahorro (10% del precio normal).
    """
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        # Modelo desconocido: usar precio de referencia conservador
        pricing = MODEL_PRICING["claude-sonnet-4-6"]

    M = 1_000_000  # tokens por millón

    # Los tokens de input que se cobran a precio normal
    # son los que NO están en caché ni en cache_creation
    billable_input = max(0, input_tokens - cache_creation_tokens - cache_read_tokens)

    input_cost = (billable_input / M) * pricing["input"]
    output_cost = (output_tokens / M) * pricing["output"]
    cache_cost = (
        (cache_creation_tokens / M) * pricing["cache_creation"]
        + (cache_read_tokens / M) * pricing["cache_read"]
    )

    total = input_cost + output_cost + cache_cost

    return CostBreakdown(
        input=round(input_cost, 8),
        output=round(output_cost, 8),
        cache=round(cache_cost, 8),
        total=round(total, 8),
    )

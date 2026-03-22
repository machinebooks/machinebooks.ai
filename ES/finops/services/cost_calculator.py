# Extraído de: LibroFinOps/cap-02-anatomia-coste.md
# services/cost_calculator.py
# Calcula el coste en USD de una llamada a LLM con soporte completo
# de prompt caching asimétrico (precio entrada ≠ precio caché ≠ precio salida).

from dataclasses import dataclass
from typing import Optional
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class CallCostBreakdown:
    """Desglose completo del coste de una llamada, en USD."""
    input_tokens: int
    output_tokens: int
    cached_input_tokens: int       # Tokens servidos desde caché (precio reducido)
    cache_write_tokens: int        # Tokens escritos en caché (algunos proveedores cobran)

    input_cost_usd: float          # Coste de tokens de entrada no cacheados
    output_cost_usd: float         # Coste de tokens de salida
    cached_input_cost_usd: float   # Coste de tokens de entrada desde caché
    cache_write_cost_usd: float    # Coste de escritura de caché

    total_cost_usd: float          # Suma de todos los componentes
    total_cost_eur: float          # Total en EUR (con tipo de cambio del día)

    model_id: str
    provider: str
    cache_savings_usd: float       # Cuánto se ahorró por usar caché vs. precio estándar


def calculate_call_cost(
    pricing: LLMModelPricing,
    input_tokens: int,
    output_tokens: int,
    cached_input_tokens: int = 0,
    cache_write_tokens: int = 0,
    eur_exchange_rate: float = 0.92  # USD → EUR; actualizar periódicamente
) -> CallCostBreakdown:
    """
    Calcula el coste completo de una llamada LLM con desglose por tipo de token.

    Los tokens de entrada se dividen en:
    - input_tokens: procesados a precio estándar (input_price_per_1m)
    - cached_input_tokens: servidos desde caché (cached_input_price_per_1m)
    - cache_write_tokens: escritos en caché (cache_write_price_per_1m)

    La API de Anthropic devuelve estos tres contadores en usage.
    """
    MILLION = 1_000_000

    # Tokens de entrada estándar (los que NO vienen de caché)
    standard_input_tokens = input_tokens - cached_input_tokens - cache_write_tokens
    standard_input_tokens = max(0, standard_input_tokens)

    # Cálculo por componente
    input_cost = (standard_input_tokens / MILLION) * pricing.input_price_per_1m
    output_cost = (output_tokens / MILLION) * pricing.output_price_per_1m

    cached_price = pricing.cached_input_price_per_1m or pricing.input_price_per_1m
    cached_cost = (cached_input_tokens / MILLION) * cached_price

    write_price = pricing.cache_write_price_per_1m or 0.0
    write_cost = (cache_write_tokens / MILLION) * write_price

    total_usd = input_cost + output_cost + cached_cost + write_cost
    total_eur = total_usd * eur_exchange_rate

    # Ahorro por caché: diferencia entre precio estándar y precio cacheado
    cache_savings = (cached_input_tokens / MILLION) * (
        pricing.input_price_per_1m - cached_price
    )

    return CallCostBreakdown(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cached_input_tokens=cached_input_tokens,
        cache_write_tokens=cache_write_tokens,
        input_cost_usd=round(input_cost, 8),
        output_cost_usd=round(output_cost, 8),
        cached_input_cost_usd=round(cached_cost, 8),
        cache_write_cost_usd=round(write_cost, 8),
        total_cost_usd=round(total_usd, 8),
        total_cost_eur=round(total_eur, 8),
        model_id=pricing.model_id,
        provider=pricing.provider,
        cache_savings_usd=round(cache_savings, 8),
    )

# Extraído de: LibroFinOps/cap-09-cache-prompt-batch.md
# models/llm_usage_log.py (extensión del Capítulo 4)
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean

class LLMUsageLog(Base):
    """Log extendido con campos de prompt caching y batch."""
    __tablename__ = "llm_usage_log"

    id                     = Column(Integer, primary_key=True)
    service_name           = Column(String(100))
    model                  = Column(String(100))
    input_tokens           = Column(Integer)
    output_tokens          = Column(Integer)
    # Campos de caching (0 si no se usó caching)
    cache_read_tokens      = Column(Integer, default=0)
    cache_creation_tokens  = Column(Integer, default=0)
    # Coste real (con descuentos de caché y/o batch)
    cost_usd               = Column(Float)
    # Coste hipotético sin ninguna optimización (para calcular ahorro acumulado)
    cost_without_cache_usd = Column(Float, nullable=True)
    created_at             = Column(DateTime)
    user_id                = Column(String(100), nullable=True)
    is_batch               = Column(Boolean, default=False)


def calculate_cost_with_cache(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_read_tokens: int = 0,
    cache_creation_tokens: int = 0,
    is_batch: bool = False,
) -> tuple[float, float]:
    """
    Calcula el coste real aplicando descuentos de caché y batch.
    Devuelve (cost_actual, cost_without_optimizations).
    """
    PRICES = {
        "claude-sonnet-4-6": {
            "input": 3.00, "output": 15.00,
            "cache_write": 3.75, "cache_read": 0.30,
        },
        "claude-haiku-4-5": {
            "input": 0.80, "output": 4.00,
            "cache_write": 1.00, "cache_read": 0.08,
        },
        "claude-opus-4-6": {
            "input": 15.00, "output": 75.00,
            "cache_write": 18.75, "cache_read": 1.50,
        },
    }

    p = PRICES.get(model, PRICES["claude-sonnet-4-6"])
    M = 1_000_000

    # Tokens de entrada normales (ni cacheados ni en caché de escritura)
    normal_input = input_tokens - cache_read_tokens - cache_creation_tokens
    batch_factor = 0.50 if is_batch else 1.00

    cost_actual = batch_factor * (
        normal_input            / M * p["input"]
        + cache_creation_tokens / M * p["cache_write"]
        + cache_read_tokens     / M * p["cache_read"]
        + output_tokens         / M * p["output"]
    )

    # Coste base sin ninguna optimización (solo para comparación)
    cost_without = (
        input_tokens  / M * p["input"]
        + output_tokens / M * p["output"]
    )

    return cost_actual, cost_without

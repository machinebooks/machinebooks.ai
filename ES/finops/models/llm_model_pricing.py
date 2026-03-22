# Extraído de: LibroFinOps/cap-01-la-factura.md
# models/llm_model_pricing.py
from sqlalchemy import Column, Integer, String, Float, Boolean
from app.database import Base

class LLMModelPricing(Base):
    """Catálogo de precios por modelo. Editable por admin."""
    __tablename__ = "llm_model_pricing"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_type = Column(String(30), nullable=False)
    model_name = Column(String(100), nullable=False, unique=True)
    input_price_per_1m = Column(Float, nullable=False)   # USD por 1M tokens
    output_price_per_1m = Column(Float, nullable=False)  # USD por 1M tokens
    is_active = Column(Boolean, default=True)

    def calculate_cost(
        self, prompt_tokens: int, completion_tokens: int
    ) -> tuple[float, float, float]:
        """Calcula coste de una llamada. Retorna (input, output, total)."""
        cost_in = (prompt_tokens / 1_000_000) * self.input_price_per_1m
        cost_out = (completion_tokens / 1_000_000) * self.output_price_per_1m
        return cost_in, cost_out, cost_in + cost_out

# Extraído de: LibroTecnico/cap-11-integracion-llms.md
# Ejemplo didáctico: patrones/ai_service/models/llm_pricing.py
class LLMModelPricing(Base):
    """
    Precios por token configurables desde panel Admin.
    Se usa para calcular el campo cost_eur en LLMUsageLog.
    """
    __tablename__ = "llm_model_pricing"

    id = Column(Integer, primary_key=True)
    provider = Column(String(32), nullable=False)
    model_id = Column(String(64), nullable=False)

    # Precios en EUR por millón de tokens (ajustar según tasa de cambio)
    input_price_per_million = Column(Float, nullable=False)
    output_price_per_million = Column(Float, nullable=False)

    # Cache pricing: algunos proveedores descuentan tokens en caché
    cached_input_price_per_million = Column(Float)
    supports_cache_pricing = Column(Boolean, default=False)

    effective_from = Column(DateTime, nullable=False)
    effective_to = Column(DateTime)  # NULL = precio activo
    updated_by = Column(String(36))  # Auditoría de cambios de precio

    def calculate_cost(self, input_tokens: int, output_tokens: int,
                       cached_tokens: int = 0) -> float:
        """Calcula el coste en EUR para un uso concreto."""
        input_cost = (input_tokens - cached_tokens) * \
                     self.input_price_per_million / 1_000_000

        cache_cost = cached_tokens * \
                     (self.cached_input_price_per_million or
                      self.input_price_per_million) / 1_000_000

        output_cost = output_tokens * \
                      self.output_price_per_million / 1_000_000

        return input_cost + cache_cost + output_cost

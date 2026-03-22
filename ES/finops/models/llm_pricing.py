# Extraído de: LibroFinOps/cap-22-multiproveedor.md
# models/llm_pricing.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from datetime import datetime
from database import Base


class LLMModelPricing(Base):
    """
    Tabla central de proveedores y modelos disponibles.
    Ningún proveedor está hardcodeado en el código de aplicación.
    """
    __tablename__ = "llm_model_pricing"

    id = Column(Integer, primary_key=True)
    provider = Column(String(50), nullable=False)         # "anthropic" | "azure_openai"
    model_id = Column(String(100), nullable=False)        # ID interno del proveedor
    display_name = Column(String(100))                    # Nombre para UI
    api_endpoint = Column(String(200))                    # URL del endpoint
    api_version = Column(String(20))                      # Para Azure: versión de la API

    # Pricing (en USD por millón de tokens)
    price_input_per_1m = Column(Float, nullable=False)
    price_output_per_1m = Column(Float, nullable=False)
    price_last_updated = Column(DateTime, default=datetime.utcnow)

    # Capacidades del modelo
    max_context_tokens = Column(Integer)
    supports_function_calling = Column(Boolean, default=False)
    supports_vision = Column(Boolean, default=False)
    supports_streaming = Column(Boolean, default=True)

    # Estado y configuración
    active = Column(Boolean, default=False)               # ¿recibe tráfico?
    is_default = Column(Boolean, default=False)
    priority = Column(Integer, default=10)                # menor = primero
    health_status = Column(String(20), default="unknown") # healthy | degraded | down

    # Committed use
    committed_use_discount = Column(Float)                # 0.22 = 22%
    contract_end_date = Column(DateTime)

    # Metadatos para routing
    latency_p95_ms = Column(Float)
    quality_score_avg = Column(Float)
    suitable_for_tasks = Column(JSON)                     # task_types recomendados
    not_suitable_for_tasks = Column(JSON)                 # task_types excluidos

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

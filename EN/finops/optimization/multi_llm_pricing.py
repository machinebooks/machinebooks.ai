# Source: The FinOps Engineer and the Machine -- Chapter 22
# Pattern: Multi-provider pricing model

# models/llm_pricing.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from datetime import datetime
from database import Base


class LLMModelPricing(Base):
    """
    Central table of available providers and models.
    No provider is hardcoded in the application code.
    """
    __tablename__ = "llm_model_pricing"

    id = Column(Integer, primary_key=True)
    provider = Column(String(50), nullable=False)         # "anthropic" | "azure_openai"
    model_id = Column(String(100), nullable=False)        # Provider's internal ID
    display_name = Column(String(100))                    # Name for UI
    api_endpoint = Column(String(200))                    # Endpoint URL
    api_version = Column(String(20))                      # For Azure: API version

    # Pricing (in USD per million tokens)
    price_input_per_1m = Column(Float, nullable=False)
    price_output_per_1m = Column(Float, nullable=False)
    price_last_updated = Column(DateTime, default=datetime.utcnow)

    # Model capabilities
    max_context_tokens = Column(Integer)
    supports_function_calling = Column(Boolean, default=False)
    supports_vision = Column(Boolean, default=False)
    supports_streaming = Column(Boolean, default=True)

    # Status and configuration
    active = Column(Boolean, default=False)               # Receives traffic?
    is_default = Column(Boolean, default=False)
    priority = Column(Integer, default=10)                # lower = first
    health_status = Column(String(20), default="unknown") # healthy | degraded | down

    # Committed use
    committed_use_discount = Column(Float)                # 0.22 = 22%
    contract_end_date = Column(DateTime)

    # Routing metadata
    latency_p95_ms = Column(Float)
    quality_score_avg = Column(Float)
    suitable_for_tasks = Column(JSON)                     # recommended task_types
    not_suitable_for_tasks = Column(JSON)                 # excluded task_types

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

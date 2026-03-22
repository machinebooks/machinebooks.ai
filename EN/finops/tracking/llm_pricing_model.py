# Source: The FinOps Engineer and the Machine -- Chapter 2
# Pattern: LLMModelPricing with cache pricing fields

# models/llm_pricing.py
# SQLAlchemy model for the LLM pricing master table.
# This is the single source of truth used by all tracking components.

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class LLMModelPricing(Base):
    """
    Master pricing table per model and provider.
    Maintains history: records are not deleted, is_active is set to False.
    Prices are expressed in USD per million tokens.
    """
    __tablename__ = "llm_model_pricing"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Model identification
    provider = Column(String(50), nullable=False, index=True)
    # E.g.: "anthropic", "openai", "azure_openai", "ollama"
    model_id = Column(String(100), nullable=False, index=True)
    # E.g.: "claude-sonnet-4-6", "gpt-4o", "text-embedding-3-small"
    model_display_name = Column(String(200), nullable=True)

    # Prices in USD per million tokens
    input_price_per_1m = Column(Float, nullable=False, default=0.0)
    output_price_per_1m = Column(Float, nullable=False, default=0.0)

    # Prompt caching prices (Anthropic and some other providers)
    cached_input_price_per_1m = Column(Float, nullable=True, default=None)
    # Cost of writing tokens to cache (if the provider charges separately)
    cache_write_price_per_1m = Column(Float, nullable=True, default=None)

    # Model type (for segmenting analysis)
    model_type = Column(String(30), nullable=False, default="chat")
    # Values: "chat", "embedding", "vision", "audio"

    # Validity control
    effective_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_active = Column(Boolean, nullable=False, default=True)

    # Change traceability
    updated_by = Column(String(100), nullable=True)
    change_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow,
                       onupdate=datetime.utcnow)

    def __repr__(self):
        return (f"<LLMModelPricing provider={self.provider!r} "
                f"model={self.model_id!r} active={self.is_active}>")

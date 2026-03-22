# Source: The FinOps Engineer and the Machine -- Chapter 8
# Pattern: LLM service configuration model

# models/llm_config.py
from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class ModelTier(str, enum.Enum):
    """Model tiers available on the Platform."""
    FAST = "fast"          # claude-haiku-4-5: classification and extraction
    BALANCED = "balanced"  # claude-sonnet-4-6: guided generation
    POWERFUL = "powerful"  # claude-opus-4-6: complex reasoning

# Tier-to-model map — updatable without code changes
TIER_TO_MODEL: dict[ModelTier, str] = {
    ModelTier.FAST:     "claude-haiku-4-5",
    ModelTier.BALANCED: "claude-sonnet-4-6",
    ModelTier.POWERFUL: "claude-opus-4-6",
}

class LLMServiceConfig(Base):
    """Routing table: which model each service uses."""
    __tablename__ = "llm_service_config"

    service_name = Column(String(100), primary_key=True)
    # Default tier for this service
    default_tier  = Column(Enum(ModelTier), default=ModelTier.BALANCED)
    # If True, the heuristic classifier can upgrade the tier
    allow_upgrade  = Column(Boolean, default=False)
    # If True, the heuristic classifier can downgrade the tier
    allow_downgrade = Column(Boolean, default=True)
    # Output token limit for this service
    max_output_tokens = Column(String(10), default="1024")
    updated_at = Column(DateTime)
    updated_by = Column(String(100))

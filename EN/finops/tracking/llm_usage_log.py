# Source: The FinOps Engineer and the Machine -- Chapter 1
# Pattern: LLMUsageLog model -- atomic record per LLM call

# models/llm_usage_log.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base

class LLMUsageLog(Base):
    """Atomic record of each LLM call.
    One record per invocation, without exception."""
    __tablename__ = "llm_usage_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    service_type = Column(
        String(50), nullable=False  # "chat", "rag", "agent", "batch"
    )
    provider_type = Column(
        String(30), nullable=False  # "anthropic", "azure_openai", "ollama"
    )
    model_name = Column(
        String(100), nullable=False  # "claude-sonnet-4-6"
    )
    prompt_tokens = Column(Integer, nullable=False, default=0)
    completion_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)
    cost_input = Column(Float, nullable=False, default=0.0)   # USD
    cost_output = Column(Float, nullable=False, default=0.0)  # USD
    cost_total = Column(Float, nullable=False, default=0.0)   # USD
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(
        DateTime, server_default=func.now(), index=True
    )

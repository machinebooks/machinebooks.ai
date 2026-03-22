# Source: The FinOps Engineer and the Machine -- Chapter 4
# Pattern: Full LLMUsageLog model (28 fields)

# models/llm_usage_log.py
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Index
from sqlalchemy.dialects.mysql import CHAR
from datetime import datetime, timezone
import uuid
from .base import Base

class LLMUsageLog(Base):
    """
    Complete record of each LLM call.
    Captures both cost data (production fields)
    and analysis context (debug fields).
    """
    __tablename__ = "llm_usage_logs"

    # --- Temporal identity ---
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    request_id = Column(String(64), nullable=True, index=True)  # correlation with APM/tracing

    # --- Semantic attribution ---
    calling_app = Column(String(128), nullable=False, index=True)   # origin module
    service_name = Column(String(128), nullable=False, index=True)  # specific operation
    user_id = Column(String(64), nullable=True, index=True)         # user who triggered the call
    prompt_key = Column(String(128), nullable=True)                 # prompt version/name

    # --- Model and provider ---
    model = Column(String(128), nullable=False, index=True)    # e.g. claude-sonnet-4-6
    provider = Column(String(64), nullable=False, index=True)  # anthropic, openai, azure

    # --- Token consumption ---
    input_tokens = Column(Integer, default=0, nullable=False)
    output_tokens = Column(Integer, default=0, nullable=False)
    cache_creation_tokens = Column(Integer, default=0, nullable=False)  # prompt caching: write
    cache_read_tokens = Column(Integer, default=0, nullable=False)       # prompt caching: read
    total_tokens = Column(Integer, default=0, nullable=False)

    # --- Calculated cost (USD) ---
    input_cost_usd = Column(Float, default=0.0, nullable=False)
    output_cost_usd = Column(Float, default=0.0, nullable=False)
    cache_cost_usd = Column(Float, default=0.0, nullable=False)
    total_cost_usd = Column(Float, default=0.0, nullable=False)

    # --- RAG context ---
    rag_collection = Column(String(128), nullable=True)   # Qdrant collection queried
    rag_query = Column(Text, nullable=True)               # query that generated the context

    # --- Generation parameters ---
    temperature = Column(Float, nullable=True)
    max_tokens = Column(Integer, nullable=True)
    system_message = Column(Text, nullable=True)    # first 500 characters
    response_text = Column(Text, nullable=True)     # first 1000 characters

    # --- Performance metrics ---
    latency_ms = Column(Integer, nullable=True)     # total call time
    error_message = Column(Text, nullable=True)     # if an exception occurred

    # --- Environment ---
    environment = Column(String(32), default="prod", nullable=False, index=True)

    # --- Composite indexes for dashboard queries ---
    __table_args__ = (
        Index("idx_app_service_ts", "calling_app", "service_name", "timestamp"),
        Index("idx_user_ts", "user_id", "timestamp"),
        Index("idx_model_ts", "model", "timestamp"),
    )

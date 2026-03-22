"""
Chapter 5 + Chapter 11: AI governance models — platform_core schema.

These four models have NO equivalent in traditional CRUD applications.
Any system integrating LLMs in production needs something equivalent:

  LLMServiceConfig  — which model to use for each task (swap without redeploy)
  LLMUsageLog       — every LLM invocation traced with tokens, cost, latency
  LLMModelPricing   — per-token prices editable from Admin panel
  LLMQualityScore   — quality evaluation closing the feedback loop

All reside in platform_core (__bind_key__ = 'platform_core') to keep
AI governance data separate from business data in operations_db.
"""

from datetime import datetime, timezone
from .base_model import db


# =============================================================================
# LLMServiceConfig (Chapter 5 + Chapter 11)
# =============================================================================

class LLMServiceConfig(db.Model):
    """
    Which model to use for each AI task — change model without redeploy.

    Examples of service_type:
      'chat', 'document_analysis', 'proposal_generation',
      'intent_classification', 'cv_scoring', 'opportunity_matching'
    """
    __tablename__ = "llm_service_configs"
    __bind_key__ = "platform_core"

    id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(50), unique=True, nullable=False)
    provider = db.Column(db.String(30), nullable=False)
    # providers: anthropic, openai, azure_openai, ollama, lm_studio
    model_name = db.Column(db.String(100), nullable=False)
    # models: claude-sonnet-4-6, claude-haiku-4-5, claude-opus-4-6, gpt-4o
    temperature = db.Column(db.Float, default=0.7)
    max_tokens = db.Column(db.Integer, default=4096)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Fallback when primary provider fails (Chapter 11 — fallback chains)
    fallback_provider = db.Column(db.String(30), nullable=True)
    fallback_model = db.Column(db.String(100), nullable=True)

    # Configuration integrity — SHA-256 verified every 12h by Celery Beat
    config_hash = db.Column(db.String(64))
    last_verified_at = db.Column(db.DateTime)

    updated_by = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(
        db.DateTime, onupdate=lambda: datetime.now(timezone.utc)
    )


# =============================================================================
# LLMUsageLog (Chapter 5 + Chapter 11)
# =============================================================================

class LLMUsageLog(db.Model):
    """
    Every LLM call traced with tokens, cost, and latency.

    prompt_hash stores a SHA-256 of the prompt for traceability
    WITHOUT storing potentially sensitive prompt content in the log table.
    """
    __tablename__ = "llm_usage_logs"
    __bind_key__ = "platform_core"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)  # NULL for system tasks
    service_type = db.Column(db.String(50), nullable=False)
    provider = db.Column(db.String(30), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)

    prompt_tokens = db.Column(db.Integer, default=0)
    completion_tokens = db.Column(db.Integer, default=0)
    total_tokens = db.Column(db.Integer, default=0)

    estimated_cost_eur = db.Column(db.Float, default=0.0)
    latency_ms = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), default="success")
    # Values: success, error, timeout, rate_limited, fallback_used

    prompt_hash = db.Column(db.String(64))

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        db.Index("idx_usage_user_date", "user_id", "created_at"),
        db.Index("idx_usage_service", "service_type", "created_at"),
        db.Index(
            "idx_usage_provider_model", "provider", "model_name", "created_at"
        ),
    )


# =============================================================================
# LLMModelPricing (Chapter 5 + Chapter 11)
# =============================================================================

class LLMModelPricing(db.Model):
    """
    Per-token prices configurable from the Admin panel.
    Unique constraint on (provider, model_name, effective_from) preserves
    price history — old prices are never overwritten.
    """
    __tablename__ = "llm_model_pricing"
    __bind_key__ = "platform_core"

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(30), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    input_price_per_1k = db.Column(db.Float, nullable=False)   # EUR/1K input
    output_price_per_1k = db.Column(db.Float, nullable=False)  # EUR/1K output
    currency = db.Column(db.String(3), default="EUR")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    effective_from = db.Column(db.DateTime, nullable=False)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_by = db.Column(db.Integer, nullable=True)

    __table_args__ = (
        db.UniqueConstraint(
            "provider", "model_name", "effective_from",
            name="uq_pricing_provider_model_date",
        ),
    )


# =============================================================================
# LLMQualityScore (Chapter 11 + Chapter 19)
# =============================================================================

class LLMQualityScore(db.Model):
    """
    Quality evaluation of AI responses — closes the feedback loop.

    Seven metrics evaluated by claude-haiku-4-5 (Chapter 19 — Quality Scorer):
      hallucination, groundedness, relevance, coherence, bias, toxicity, pii.
    """
    __tablename__ = "llm_quality_scores"
    __bind_key__ = "platform_core"

    id = db.Column(db.Integer, primary_key=True)
    usage_log_id = db.Column(
        db.Integer, db.ForeignKey("llm_usage_logs.id"), nullable=False
    )

    hallucination_score = db.Column(db.Float)
    groundedness_score = db.Column(db.Float)
    relevance_score = db.Column(db.Float)
    coherence_score = db.Column(db.Float)
    bias_score = db.Column(db.Float)
    toxicity_score = db.Column(db.Float)
    pii_score = db.Column(db.Float)

    overall_pass = db.Column(db.Boolean)
    evaluator_model = db.Column(db.String(100), default="claude-haiku-4-5")

    evaluated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

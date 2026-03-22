# Chapter 10 — AI models: zero-hardcoding configuration
#
# All LLM configuration lives in the database, manageable from an admin panel.
# An administrator can change the model, temperature, or fallback provider
# without redeploying any service.
#
# Three tables: AIProvider, AIServiceConfig, AIPrompt
# Plus RAG management tables from Chapter 11.

import enum

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, JSON,
    ForeignKey, DateTime, Enum as SAEnum,
)
from sqlalchemy.orm import relationship

try:
    from backend.models.base import BaseModel
except ImportError:
    from base import BaseModel


# ── Enumerations ──────────────────────────────────────────────────────────

class ProviderType(str, enum.Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"


# ── AIProvider ────────────────────────────────────────────────────────────

class AIProvider(BaseModel):
    """LLM provider registered in the system.

    API keys are stored as vault references, NEVER in plain text.
    Monthly budgets enable automatic cost control.
    """
    __tablename__ = "ai_providers"

    name = Column(String(100), unique=True, nullable=False)   # "anthropic_cloud"
    display_name = Column(String(200))                         # "Anthropic (Cloud)"
    provider_type = Column(SAEnum(ProviderType), nullable=False)
    api_base_url = Column(String(500))
    api_key_ref = Column(String(200), comment="Vault reference — NEVER the real key")
    is_active = Column(Boolean, default=True)
    is_local = Column(Boolean, default=False)  # True for Ollama/LM Studio

    # Available models with pricing per million tokens
    available_models = Column(JSON)
    # Example: [{"name": "claude-sonnet-4-6", "input_price": 3.0, "output_price": 15.0}]

    last_health_check = Column(DateTime, nullable=True)
    last_latency_ms = Column(Integer, nullable=True)
    monthly_budget = Column(Float, nullable=True, comment="Monthly budget in EUR")
    monthly_spent = Column(Float, default=0.0, comment="Accumulated spend this month")

    service_configs = relationship("AIServiceConfig", back_populates="provider",
                                   foreign_keys="AIServiceConfig.provider_id")


# ── AIServiceConfig ───────────────────────────────────────────────────────

class AIServiceConfig(BaseModel):
    """Configuration for a specific AI service.

    Each row represents one AI capability: orchestrator, privacy_agent,
    risk_agent, compliance_agent, classifier, chat, report_writer, etc.

    The service-to-model mapping table from the book (Chapter 10):
    - Orchestrator       -> claude-opus-4-6     (max capability)
    - Privacy/Risk agent -> claude-sonnet-4-6   (balance)
    - Intent classifier  -> claude-haiku-4-5    (speed/cost)
    """
    __tablename__ = "ai_service_configs"

    service_name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200))
    description = Column(Text, nullable=True)

    # Primary provider and model
    provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=False)
    model_name = Column(String(200), nullable=False)
    temperature = Column(Float, default=0.3)
    max_input_tokens = Column(Integer, default=4096)
    max_output_tokens = Column(Integer, default=4096)

    # Fallback level 1: secondary cloud provider
    fallback_provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=True)
    fallback_model_name = Column(String(200), nullable=True)

    # Fallback level 2: local model (Ollama)
    local_fallback_provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=True)
    local_fallback_model_name = Column(String(200), nullable=True)

    # Service-specific guardrails (JSON)
    guardrails = Column(JSON, default=dict)
    # Example: {"max_input_chars": 8000, "prompt_injection_check": true,
    #           "blocked_topics": ["fiscal"], "enable_pii_filter": true}

    active_prompt_id = Column(Integer, ForeignKey("ai_prompts.id"), nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    provider = relationship("AIProvider", foreign_keys=[provider_id],
                            back_populates="service_configs")
    active_prompt = relationship("AIPrompt", foreign_keys=[active_prompt_id])


# ── AIPrompt ──────────────────────────────────────────────────────────────

class AIPrompt(BaseModel):
    """Versioned system prompt for each AI service.

    Enables iterating on production prompts with instant rollback.
    """
    __tablename__ = "ai_prompts"

    service_name = Column(String(100), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    prompt_text = Column(Text, nullable=False)
    is_active = Column(Boolean, default=False)
    created_by_user = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)


# ── RAG Collections and Documents (Chapter 11) ───────────────────────────

class RAGCollection(BaseModel):
    """Vector collection in Qdrant.

    Each collection groups documents by context and embedding type.
    Dual collections: local (768d, nomic-embed-text) and cloud (3072d, text-embedding-3-large).
    Vectors are NOT interchangeable between collections.
    """
    __tablename__ = "rag_collections"

    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    embedding_provider = Column(String(20), nullable=False)  # "local" | "cloud"
    embedding_model = Column(String(100), nullable=False)
    embedding_dimensions = Column(Integer, nullable=False)
    distance_metric = Column(String(20), default="cosine")
    document_count = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)

    documents = relationship("RAGDocument", back_populates="collection")


class RAGDocument(BaseModel):
    """Regulatory document indexed in a RAG collection.

    Each document is split into N chunks, each with its vector in Qdrant.
    The file_hash enables smart re-indexing: unchanged documents are skipped.
    """
    __tablename__ = "rag_documents"

    collection_id = Column(Integer, ForeignKey("rag_collections.id"), nullable=False)
    title = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)   # "regulation" | "guide" | "standard"
    source_authority = Column(String(100))              # "EU" | "AEPD" | "CCN" | "ISO"
    source_url = Column(String(500))
    publication_date = Column(DateTime)
    file_path = Column(String(500))
    file_hash = Column(String(64), comment="SHA-256 for change detection")
    chunk_size = Column(Integer, default=512)
    chunk_overlap = Column(Integer, default=64)
    total_chunks = Column(Integer, default=0)
    status = Column(String(20), default="pending",
                    comment="pending | processing | indexed | error")
    error_message = Column(Text)

    collection = relationship("RAGCollection", back_populates="documents")

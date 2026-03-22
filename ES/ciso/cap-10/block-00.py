# Extraído de: LibroCISO/cap-10-arquitectura-llm.md
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, JSON,
    ForeignKey, DateTime, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from app.models.base import BaseModel  # Incluye id, created_at, updated_at, soft_delete
import enum


class ProviderType(str, enum.Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"


class AIProvider(BaseModel):
    """Proveedor de LLM registrado en el sistema."""
    __tablename__ = "ai_providers"

    name = Column(String(100), unique=True, nullable=False)  # "anthropic_cloud"
    display_name = Column(String(200))                        # "Anthropic (Cloud)"
    provider_type = Column(SAEnum(ProviderType), nullable=False)
    api_base_url = Column(String(500))        # URL base del endpoint
    api_key_ref = Column(String(200))          # Referencia al vault, NUNCA la clave real
    is_active = Column(Boolean, default=True)
    is_local = Column(Boolean, default=False)  # True para Ollama/LM Studio
    # Modelos disponibles con precios por millón de tokens
    available_models = Column(JSON)
    # Ejemplo: [{"name": "claude-sonnet-4-6", "input_price": 3.0, "output_price": 15.0}]
    last_health_check = Column(DateTime, nullable=True)
    last_latency_ms = Column(Integer, nullable=True)
    monthly_budget = Column(Float, nullable=True)  # Presupuesto mensual en EUR
    monthly_spent = Column(Float, default=0.0)      # Gasto acumulado del mes

    # Relaciones
    service_configs = relationship("AIServiceConfig", back_populates="provider")


class AIServiceConfig(BaseModel):
    """Configuración de un servicio de IA específico."""
    __tablename__ = "ai_service_configs"

    service_name = Column(String(100), unique=True, nullable=False)
    # Ejemplos: "orchestrator", "privacy_agent", "risk_agent",
    #           "compliance_agent", "classifier", "chat", "report_writer"
    display_name = Column(String(200))
    description = Column(Text, nullable=True)

    # Proveedor y modelo principal
    provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=False)
    model_name = Column(String(200), nullable=False)  # "claude-opus-4-6"
    temperature = Column(Float, default=0.3)
    max_input_tokens = Column(Integer, default=4096)
    max_output_tokens = Column(Integer, default=4096)

    # Fallback nivel 1: cloud secundario
    fallback_provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=True)
    fallback_model_name = Column(String(200), nullable=True)

    # Fallback nivel 2: local
    local_fallback_provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=True)
    local_fallback_model_name = Column(String(200), nullable=True)

    # Guardrails específicos del servicio (JSON)
    guardrails = Column(JSON, default=dict)
    # Ejemplo: {"max_input_chars": 8000, "prompt_injection_check": true,
    #           "blocked_topics": ["fiscal", "laboral"], "enable_pii_filter": true}

    # Prompt del sistema activo (referencia a AIPrompt)
    active_prompt_id = Column(Integer, ForeignKey("ai_prompts.id"), nullable=True)

    is_active = Column(Boolean, default=True)

    # Relaciones
    provider = relationship("AIProvider", foreign_keys=[provider_id],
                           back_populates="service_configs")
    active_prompt = relationship("AIPrompt", foreign_keys=[active_prompt_id])


class AIPrompt(BaseModel):
    """Prompt del sistema versionado para cada servicio."""
    __tablename__ = "ai_prompts"

    service_name = Column(String(100), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    prompt_text = Column(Text, nullable=False)
    is_active = Column(Boolean, default=False)
    created_by = Column(String(200), nullable=True)  # Usuario que creó esta versión
    notes = Column(Text, nullable=True)  # Notas del cambio

    # Constraint: solo un prompt activo por servicio
    # Se gestiona en lógica de aplicación al activar uno nuevo

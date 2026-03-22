# Extraído de: LibroFinOps/cap-08-routing-modelos.md
# models/llm_config.py
from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class ModelTier(str, enum.Enum):
    """Niveles de modelo disponibles en la Plataforma."""
    FAST = "fast"          # claude-haiku-4-5: clasificación y extracción
    BALANCED = "balanced"  # claude-sonnet-4-6: generación guiada
    POWERFUL = "powerful"  # claude-opus-4-6: razonamiento complejo

# Mapa de tier a modelo concreto — actualizable sin código
TIER_TO_MODEL: dict[ModelTier, str] = {
    ModelTier.FAST:     "claude-haiku-4-5",
    ModelTier.BALANCED: "claude-sonnet-4-6",
    ModelTier.POWERFUL: "claude-opus-4-6",
}

class LLMServiceConfig(Base):
    """Tabla de routing: qué modelo usa cada servicio."""
    __tablename__ = "llm_service_config"

    service_name = Column(String(100), primary_key=True)
    # Tier por defecto para este servicio
    default_tier  = Column(Enum(ModelTier), default=ModelTier.BALANCED)
    # Si True, el clasificador heurístico puede upgradear el tier
    allow_upgrade  = Column(Boolean, default=False)
    # Si True, el clasificador heurístico puede downgradear el tier
    allow_downgrade = Column(Boolean, default=True)
    # Límite de tokens de salida para este servicio
    max_output_tokens = Column(String(10), default="1024")
    updated_at = Column(DateTime)
    updated_by = Column(String(100))

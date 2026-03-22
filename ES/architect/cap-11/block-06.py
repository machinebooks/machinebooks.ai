# Extraído de: LibroTecnico/cap-11-integracion-llms.md
# Ejemplo didáctico: patrones/ai_service/models/llm_usage.py
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

class LLMUsageLog(Base):
    """
    Registro atómico de cada llamada a un modelo de lenguaje.
    Un registro por llamada, siempre, sin excepciones.
    """
    __tablename__ = "llm_usage_log"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    service_type = Column(String(64), nullable=False, index=True)
    provider = Column(String(32), nullable=False)
    model_id = Column(String(64), nullable=False)

    # Métricas de uso
    input_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    total_tokens = Column(Integer, nullable=False)
    latency_ms = Column(Integer)
    cost_eur = Column(Float)   # Calculado en tiempo real con LLMModelPricing

    # Trazabilidad
    user_id = Column(String(36), index=True)
    correlation_id = Column(String(36))    # Para correlacionar con request HTTP
    prompt_id = Column(String(64))         # Versión del prompt usada
    prompt_hash = Column(String(16))       # Verificación de integridad

    # Flags de compliance
    contained_pii = Column(Boolean, default=False)
    pii_redacted = Column(Boolean, default=False)
    privacy_restricted = Column(Boolean, default=False)  # Petición local/offline

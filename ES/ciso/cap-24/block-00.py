# Extraído de: LibroCISO/cap-24-calidad-ia.md
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Float
from sqlalchemy import Boolean, Text, DateTime, Index, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class LLMUsageLog(Base):
    """Registro granular de cada llamada LLM.

    Cada interacción con cualquier proveedor (Claude, Azure, local)
    genera una fila. El middleware de la LLM Factory lo hace
    transparente para el desarrollador.
    """
    __tablename__ = 'llm_usage_logs'

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Quién y desde dónde
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    service_type = Column(String(50), nullable=False, index=True)
    # Ej: 'privacy_agent', 'risk_agent', 'compliance_agent',
    #     'rag_query', 'copilot_chat', 'report_writer'

    # Contexto de negocio (qué entidad GRC origina la llamada)
    entity_type = Column(String(50), nullable=True)  # 'dpia', 'risk_analysis'
    entity_id = Column(Integer, nullable=True)

    # Proveedor y modelo
    provider_type = Column(String(50), nullable=False)  # 'anthropic', 'ollama'
    model_name = Column(String(100), nullable=False)     # 'claude-sonnet-4-6'

    # Tokens consumidos
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)

    # Coste calculado (USD) — se calcula automáticamente
    # a partir de la tabla llm_model_pricing
    cost_input = Column(Float, default=0.0)
    cost_output = Column(Float, default=0.0)
    cost_total = Column(Float, default=0.0)

    # Rendimiento
    latency_ms = Column(Integer, nullable=True)
    is_cached = Column(Boolean, default=False)
    is_streaming = Column(Boolean, default=False)

    # Resultado
    success = Column(Boolean, default=True)
    error_type = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)

    # Contenido para auditoría (opcional, activable por config)
    request_id = Column(String(100), nullable=True, index=True)
    prompt_key = Column(String(100), nullable=True)
    rag_collection = Column(String(100), nullable=True)
    rag_results_count = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Índices compuestos para consultas frecuentes
    __table_args__ = (
        Index('idx_usage_service_date', 'service_type', 'created_at'),
        Index('idx_usage_provider_date', 'provider_type', 'created_at'),
        Index('idx_usage_model_date', 'model_name', 'created_at'),
    )

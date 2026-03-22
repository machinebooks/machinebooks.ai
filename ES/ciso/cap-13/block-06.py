# Extraído de: LibroCISO/cap-13-orquestador-copiloto.md
# Ejemplo didáctico: patrones/models/copilot_session.py

from sqlalchemy import (
    Column, String, Integer, Float, DateTime,
    ForeignKey, Text, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from datetime import datetime

class CopilotSession(BaseModel):
    """Sesión de conversación del copiloto IA."""
    __tablename__ = "copilot_sessions"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    corporate_id = Column(String(36), ForeignKey("corporates.id"), nullable=False)
    module_context = Column(String(50), nullable=False)   # privacy, risk, compliance, general
    title = Column(String(200), default="Nueva conversación")
    total_tokens = Column(Integer, default=0)
    total_cost_eur = Column(Float, default=0.0)
    message_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relaciones
    messages = relationship("CopilotMessage", back_populates="session", lazy="dynamic")

class CopilotMessage(BaseModel):
    """Mensaje individual dentro de una sesión del copiloto."""
    __tablename__ = "copilot_messages"

    id = Column(String(36), primary_key=True)
    session_id = Column(String(36), ForeignKey("copilot_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)     # user | assistant | system
    content = Column(Text, nullable=False)
    mode = Column(SQLEnum(CopilotMode), nullable=True)          # Modo de ejecución usado
    agents_invoked = Column(JSON, nullable=True)                 # Lista de agentes usados
    execution_steps = Column(JSON, nullable=True)                # Detalle de pasos (orquestación)
    tokens_used = Column(Integer, default=0)
    cost_eur = Column(Float, default=0.0)
    duration_ms = Column(Integer, default=0)
    guardrail_flags = Column(JSON, nullable=True)                # Alertas de guardrails (si las hubo)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Relaciones
    session = relationship("CopilotSession", back_populates="messages")

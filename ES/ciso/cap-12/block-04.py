# Extraído de: LibroCISO/cap-12-agentes-especializados.md
from sqlalchemy import (
    Column, Integer, String, Text, Float,
    DateTime, JSON, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum


class TaskStatus(str, enum.Enum):
    PENDING = "pending"      # Creada, en espera de ejecución
    RUNNING = "running"      # En ejecución
    COMPLETED = "completed"  # Finalizada con éxito
    FAILED = "failed"        # Finalizada con error


class AgentTask(BaseModel):
    """Tarea de un agente con ciclo de vida completo.

    Cada invocación de un agente crea un AgentTask que
    registra quién lo pidió, qué se pidió y qué resultó.
    """
    __tablename__ = "agent_tasks"

    id = Column(Integer, primary_key=True)
    task_uuid = Column(String(36), unique=True, nullable=False)
    agent_name = Column(String(100), nullable=False, index=True)
    status = Column(
        Enum(TaskStatus),
        default=TaskStatus.PENDING,
        nullable=False
    )

    # Quién lo pidió y con qué parámetros
    requested_by = Column(Integer, ForeignKey("users.id"))
    params = Column(JSON)  # Parámetros de entrada serializados

    # Resultado
    output = Column(JSON)          # Artefacto generado
    error_message = Column(Text)   # Si falló, el motivo

    # Métricas agregadas
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    duration_ms = Column(Integer)  # Duración total en ms

    # Timestamps del ciclo de vida
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Multi-tenancy obligatorio (ver capítulo 16)
    corporate_id = Column(Integer, ForeignKey("corporates.id"),
                         nullable=False)

    # Relación con trazas detalladas
    traces = relationship("AgentTrace", back_populates="task",
                         order_by="AgentTrace.sequence")


class AgentTrace(BaseModel):
    """Traza individual de una fase de ejecución.

    Cada fase del lifecycle (gather, analyze, generate)
    genera una entrada en esta tabla. También se registran
    errores y llamadas a herramientas individuales.
    """
    __tablename__ = "agent_traces"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("agent_tasks.id"),
                    nullable=False)

    sequence = Column(Integer, nullable=False)  # Orden dentro de la tarea
    phase = Column(String(50), nullable=False)   # gather_data, analyze, etc.

    # Métricas de la fase
    duration_ms = Column(Integer)
    tokens_input = Column(Integer, default=0)
    tokens_output = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    model_used = Column(String(100))  # Modelo LLM si aplica

    # Datos de la fase (qué herramientas usó, qué datos consultó)
    phase_data = Column(JSON)

    # Timestamp preciso
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relación inversa
    task = relationship("AgentTask", back_populates="traces")

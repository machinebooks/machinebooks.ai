# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
from sqlalchemy import Column, Integer, String, JSON, Boolean, Enum, DateTime
from sqlalchemy.orm import relationship
import enum

class AgentType(enum.Enum):
    ASSISTANT = "assistant"
    AUTONOMOUS = "autonomous"
    WORKFLOW = "workflow"
    SPECIALIZED = "specialized"

class ExecutionMode(enum.Enum):
    CHAT_RAG = "chat_rag"         # Consultas informativas con RAG
    AGENT_TOOLS = "agent_tools"   # Ejecución con herramientas
    ORCHESTRATE = "orchestrate"   # Activación de workflow predefinido

class AgentDefinition(Base):
    __tablename__ = "agent_definitions"

    id = Column(Integer, primary_key=True)
    slug = Column(String(100), unique=True, nullable=False)  # Auto-generado desde name
    name = Column(String(200), nullable=False)
    agent_type = Column(Enum(AgentType), nullable=False)
    execution_mode = Column(Enum(ExecutionMode), nullable=False)

    # Configuración del modelo
    model_id = Column(String(100), default="claude-sonnet-4-6")
    temperature = Column(Float, default=0.3)
    max_tokens = Column(Integer, default=4096)

    # System prompt y comportamiento
    system_prompt = Column(Text)
    intent_keywords = Column(JSON)  # Para auto-routing desde el clasificador

    # Estado del agente en el ciclo de vida
    status = Column(Enum("draft", "active", "archived"), default="draft")
    is_template = Column(Boolean, default=False)

    # Relación M2M con herramientas
    tool_assignments = relationship(
        "AgentToolAssignment",
        back_populates="agent",
        order_by="AgentToolAssignment.execution_order"
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class AgentToolAssignment(Base):
    """Asignación M2M de herramientas a agentes con orden y configuración específica."""
    __tablename__ = "agent_tool_assignments"

    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey("agent_definitions.id"))
    tool_name = Column(String(100))       # Nombre en el tool_registry
    execution_order = Column(Integer)     # Orden de presentación a Claude
    tool_config = Column(JSON)            # Configuración específica para este agente
    is_required = Column(Boolean, default=False)

    agent = relationship("AgentDefinition", back_populates="tool_assignments")
